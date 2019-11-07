from core import Context, Library, CallableValue
from core.events import MusicEvent
from typing import List, Dict, Iterable, ItemsView, ValuesView
from parser.abstract_syntax_tree import Node
from audio import MidiPlayer, AsyncMidiPlayer
from asyncio import Future, sleep, wait, FIRST_COMPLETED, create_task

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


def register_key ( context : Context, key : Node, expression : Node, toggle : bool = False, hold : bool = False ):
    key_value = key.eval( context )
    
    keys = context.symbols.lookup_internal( "keyboard\\keys" )

    action = KeyAction( 
        key = KeyStroke.parse( key_value.value ), 
        expr = expression,
        toggle = toggle,
        hold = hold
    )

    keys[ action.key ] = action

def register_key_toggle ( context : Context, key : Node, expression : Node ):
    register_key( context, key, expression, toggle = True )

def register_key_hold ( context : Context, key : Node, expression : Node ):
    register_key( context, key, expression, hold = True )

def keyboard_close ( context : Context ):
    keyboard : KeyboardLibrary = context.library( KeyboardLibrary )

    keyboard.close()

class KeyAction:
    def __init__ ( self, key : KeyStroke, expr : Node, hold : bool = False, toggle : bool = False, repeat : bool = False ):
        self.key : KeyStroke = key 
        self.expr : Node = expr
        self.hold : bool = hold
        self.toggle : bool = toggle
        self.repeat : bool = repeat

        self.is_active : bool = False
        self.is_pressed : bool = False

        self.async_player : AsyncMidiPlayer = None

    def play ( self, context : Context, player : MidiPlayer ):
        forked_context : Context = None

        def eval ():
            nonlocal forked_context

            now = player.get_time() if forked_context == None else forked_context.cursor

            forked_context = context.fork( cursor = now )

            value = self.expr.eval( forked_context )

            if value != None and value.is_music:
                return value
            elif value != None and isinstance( value, CallableValue ):
                value = value.call( forked_context )

                if value != None and value.is_music:
                    return value

            return None

        self.async_player = AsyncMidiPlayer( eval, player, 0, self.repeat )

        create_task( self.async_player.start() )

    def stop ( self, context : Context, player : MidiPlayer ):
        if self.async_player != None:
            create_task( self.async_player.stop() )

        self.async_player = None

    def on_press ( self, context : Context, player : MidiPlayer ):
        print("on press", self.is_pressed)
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
        print("on release", self.is_pressed)

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
        context = self.context

        self.assign_internal( "keys", dict() )

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
        if key in registered:
            registered[ key ].start( self.context, self.player )
        
    def stop ( self, key : KeyStroke ):
        if key in registered:
            registered[ key ].stop( self.context, self.player )

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
