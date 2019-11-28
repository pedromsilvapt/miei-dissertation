from core import Context, Library, Value, CallableValue, Music
from core.events import MusicEvent, NoteEvent, NoteOnEvent, NoteOffEvent
from typing import List, Dict, Iterable, ItemsView, ValuesView
from parser.abstract_syntax_tree import Node, MusicSequenceNode
from parser.abstract_syntax_tree.expressions import BoolLiteralNode
from audio import MidiPlayer, AsyncMidiPlayer
from asyncio import Future, sleep, wait, FIRST_COMPLETED, create_task
from asyncio import Event

class KeyStroke:
    def parse ( s ):
        parts = s.strip().split( "+" )

        key = parts[ -1 ]

        mods = [ s.strip().lower() for s in parts[ :-1 ] ]

        ctrl = 'ctrl' in mods
        alt = 'alt' in mods
        shift = 'shift' in mods

        return KeyStroke( ctrl, alt, shift, key )

    def __init__ ( self, ctrl, alt, shift, key ):
        self.ctrl = ctrl
        self.alt = alt
        self.shift = shift
        self.key = key

    def __eq__ ( self, k ):
        if k == None:
            return False
        
        return self.ctrl == k.ctrl \
           and self.alt == k.alt \
           and self.shift == k.shift \
           and self.key == k.key

    def __hash__ ( self ):
        return str( self ).__hash__()

    def __str__ ( self ):
        mods = list()

        if self.ctrl: mods.append( 'ctrl' )
        if self.alt: mods.append( 'alt' )
        if self.shift: mods.append( 'shift' )

        mods.append( self.key )

        return '+'.join( mods )

def get_keyboard_flag ( context : Context, node : Node, name : str, global_flags : Dict[str, int] ) -> bool:
    if node != None:
        value : Value = node.eval( context )

        return bool( value )

    return name in global_flags and global_flags[ name ] > 0

def register_key ( context : Context, key : Node, expression : Node, toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None ):
    global_flags = context.symbols.lookup_internal( "keyboard\\global_flags" );
    global_prefixes = context.symbols.lookup_internal( "keyboard\\global_prefixes" );

    toggle_value = get_keyboard_flag( context, toggle, "toggle", global_flags )
    hold_value = get_keyboard_flag( context, hold, "hold", global_flags )
    repeat_value = get_keyboard_flag( context, repeat, "repeat", global_flags )
    extend_value = get_keyboard_flag( context, extend, "extend", global_flags )

    key_value = key.eval( context )
    
    keys = context.symbols.lookup_internal( "keyboard\\keys" )

    if global_prefixes:
        expression = MusicSequenceNode( [ *global_prefixes, expression ] )

    action = KeyAction( 
        key = KeyStroke.parse( key_value ), 
        expr = expression,
        context = context,
        toggle = toggle_value,
        hold = hold_value,
        repeat = repeat_value,
        extend = extend_value,
    )

    keys[ action.key ] = action

def push_flags ( context : Context, *flags : List[Node] ):
    global_flags = context.symbols.lookup_internal( "keyboard\\global_flags" );

    for flag in flags:
        value : str = flag.eval( context )

        if Value.typeof( value ) == str:
            if value in global_flags:
                global_flags[ value ] += 1
            else:
                global_flags[ value ] = 1

def pop_flags ( context : Context, *flags : List[Node] ):
    global_flags = context.symbols.lookup_internal( "keyboard\\global_flags" );

    for flag in flags:
        value : str = flag.eval( context )

        if Value.typeof( value ) == str:
            if value in global_flags:
                global_flags[ value ] -= 1

                if global_flags[ value ] == 0:
                    del global_flags[ value ]

def push_prefix ( context : Context, expression : Node ):
    global_prefixes : List[Node] = context.symbols.lookup_internal( "keyboard\\global_prefixes" );

    global_prefixes.append( expression )

def pop_prefix ( context : Context, *flags : List[Node] ):
    global_prefixes : List[Node] = context.symbols.lookup_internal( "keyboard\\global_prefixes" );

    global_prefixes.pop()

def register_key_toggle ( context : Context, key : Node, expression : Node ):
    register_key( context, key, expression, toggle = BoolLiteralNode( True ) )

def register_key_hold ( context : Context, key : Node, expression : Node ):
    register_key( context, key, expression, hold = BoolLiteralNode( True ) )

def keyboard_close ( context : Context ):
    keyboard : KeyboardLibrary = context.library( KeyboardLibrary )

    keyboard.close()

class KeyAction:
    def __init__ ( self, key : KeyStroke, expr : Node, context : Context, hold : bool = False, toggle : bool = False, repeat : bool = False, extend : bool = False ):
        self.key : KeyStroke = key 
        self.expr : Node = expr
        self.context : Context = context
        self.hold : bool = hold
        self.toggle : bool = toggle
        self.repeat : bool = repeat
        self.extend : bool = extend

        self.is_active : bool = False
        self.is_pressed : bool = False

        self.async_player : AsyncMidiPlayer = None
        # self.extend_event : Event = Event()
        # self.extended : List[NoteOffEvent] = []
        # self.extended_player : MidiPlayer = None

    # def extend_notes ( self, player : MidiPlayer, events ):
    #     self.extended.clear()
    #     self.extended_player = player

    #     for event in events:
    #         if isinstance( event, NoteEvent ):
    #             self.extended.append( event.note_off )

    #             yield event.note_on
    #         elif isinstance( event, NoteOffEvent ):
    #             self.extended.append( event.note_off )
    #         else:
    #             yield event

    def play ( self, context : Context, player : MidiPlayer ):
        forked_context : Context = None

        def eval ():
            nonlocal forked_context

            # self.extend_event.clear()

            now = player.get_time() if forked_context == None else forked_context.cursor

            forked_context = self.context.fork( cursor = now )
            
            value = self.expr.eval( forked_context )

            if isinstance( value, Music ):
                return value
            elif callable( value ):
                value = value.call( forked_context )

                if isinstance( value, Music ):
                    return value

            return None

        self.async_player = AsyncMidiPlayer( eval, player, 0, self.repeat and not self.extend, self.extend )

        create_task( self.async_player.start() )

    def stop ( self, context : Context, player : MidiPlayer ):
        if self.async_player != None:
            create_task( self.async_player.stop() )

        self.async_player = None

    def on_press ( self, context : Context, player : MidiPlayer ):
        if self.is_pressed:
            return

        self.is_pressed = True

        if self.toggle:
            if self.async_player != None and self.async_player.is_playing:
                self.stop( context, player )
            else:
                self.play( context, player )
        else:
            self.play( context, player )

    def on_release ( self, context : Context, player : MidiPlayer ):
        if not self.is_pressed:
            return

        self.is_pressed = False

        if self.hold:
            self.stop( context, player )

class KeyboardLibrary(Library):
    def __init__ ( self, player : MidiPlayer ):
        super().__init__( "keyboard" )

        self.player : MidiPlayer = player
    
    def on_link ( self ):
        self.assign_internal( "keys", dict() )
        self.assign_internal( "global_flags", dict() )
        self.assign_internal( "global_prefixes", list() )

        self.assign( "push_flags", CallableValue( push_flags ) )
        self.assign( "pop_flags", CallableValue( pop_flags ) )
        self.assign( "push_prefix", CallableValue( push_prefix ) )
        self.assign( "pop_prefix", CallableValue( pop_prefix ) )
        self.assign( "register", CallableValue( register_key ) )
        self.assign( "register_hold", CallableValue( register_key_hold ) )
        self.assign( "register_toggle", CallableValue( register_key_toggle ) )
        self.assign( "close", CallableValue( keyboard_close ) )
        
    @property
    def registered ( self ) -> Dict[KeyStroke, KeyAction]:
        return self.lookup_internal( "keys" )

    @property
    def actions ( self ) -> ValuesView[KeyAction]:
        return self.registered.values()

    @property
    def keys ( self ) -> ItemsView[KeyStroke, KeyAction]:
        return self.registered.items()

    @property
    def pressed ( self ) -> Iterable[KeyAction]:
        return ( action for action in self.actions if action.is_active )

    @property
    def pressed_keys ( self ) -> Iterable[KeyStroke]:
        return ( action.key for action in self.pressed )

    def close ( self ):
        for action in self.actions:
            action.stop( self.context, self.player )

        close_future : Future = self.lookup_internal( "close_future" )
        
        if close_future != None:
            close_future.set_result( None )

    def start ( self, key : KeyStroke ):
        if key in self.registered:
            self.registered[ key ].start( self.context, self.player )
        
    def stop ( self, key : KeyStroke ):
        if key in self.registered:
            self.registered[ key ].stop( self.context, self.player )

    def on_press ( self, key : KeyStroke ):
        registered = self.registered

        if key in registered:
            registered[ key ].on_press( self.context, self.player )

    def on_release ( self, key : KeyStroke ):
        registered = self.registered

        if key in registered:
            registered[ key ].on_release( self.context, self.player )

    async def join_async ( self ):
        close_future : Future = self.lookup_internal( "close_future" )

        if close_future == None:
            close_future = Future()

            self.assign_internal( "close_future", close_future )
        
        await close_future
