from core import Context, Library, Value, CallableValue, Music
from core.callable_python_value import CallablePythonValue
from core.events import MusicEvent, NoteEvent, NoteOnEvent, NoteOffEvent
from typing import List, Dict, Iterable, ItemsView, ValuesView, Union, Optional, Iterator, Tuple
from parser.abstract_syntax_tree import Node, MusicSequenceNode
from parser.abstract_syntax_tree.expressions import BoolLiteralNode
from audio import MidiPlayer, AsyncMidiPlayer
from asyncio import Future, sleep, wait, FIRST_COMPLETED, create_task
from asyncio import Event
from fractions import Fraction

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
        
    def play ( self, context : Context, player : MidiPlayer ):
        forked_context : Context = None

        def eval ():
            nonlocal forked_context

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

class Keyboard:
    def __init__ ( self, context : Context, player : MidiPlayer ):
        self.context : Context = context
        self.player : MidiPlayer = player

        self.keys : Dict[KeyStroke, KeyAction] = dict()
        self.global_flags : Dict[str, int] = dict()
        self.global_prefixes : List[Node] = list()

    def get_keyboard_flag ( self, context : Context, node : Node, name : str ) -> bool:
        if node != None:
            value : Value = node.eval( context )

            return bool( value )

        return name in self.global_flags and self.global_flags[ name ] > 0

    def register_key ( self, context : Context, key : Node, expression : Node, toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None ):
        toggle_value = self.get_keyboard_flag( context, toggle, "toggle" )
        hold_value = self.get_keyboard_flag( context, hold, "hold" )
        repeat_value = self.get_keyboard_flag( context, repeat, "repeat" )
        extend_value = self.get_keyboard_flag( context, extend, "extend" )

        key_value = key.eval( context )

        if self.global_prefixes:
            expression = MusicSequenceNode( [ *self.global_prefixes, expression ] )

        action = KeyAction( 
            key = KeyStroke.parse( key_value ), 
            expr = expression,
            context = context,
            toggle = toggle_value,
            hold = hold_value,
            repeat = repeat_value,
            extend = extend_value,
        )

        self.keys[ action.key ] = action

    def push_flags ( self, context : Context, *flags : Node ):
        for flag in flags:
            value : str = flag.eval( context )

            if Value.typeof( value ) == str:
                if value in self.global_flags:
                    self.global_flags[ value ] += 1
                else:
                    self.global_flags[ value ] = 1

    def pop_flags ( self, context : Context, *flags : Node ):
        for flag in flags:
            value : str = flag.eval( context )

            if Value.typeof( value ) == str:
                if value in self.global_flags:
                    self.global_flags[ value ] -= 1

                    if self.global_flags[ value ] == 0:
                        del self.global_flags[ value ]

    def push_prefix ( self, context : Context, expression : Node ):
        self.global_prefixes.append( expression )

    def pop_prefix ( self, context : Context ):
        self.global_prefixes.pop()

    def register_key_toggle ( self, context : Context, key : Node, expression : Node ):
        return self.register_key( context, key, expression, toggle = BoolLiteralNode( True ) )

    def register_key_hold ( self, context : Context, key : Node, expression : Node ):
        return self.register_key( context, key, expression, hold = BoolLiteralNode( True ) )

    def start_all ( self ):
        for key in self.keys.values():
            key.start( self.context, self.player )
    
    def stop_all ( self ):
        for key in self.keys.values():
            key.stop( self.context, self.player )

    def start ( self, key : KeyStroke ):
        if key in self.keys:
            self.keys[ key ].start( self.context, self.player )
        
    def stop ( self, key : KeyStroke ):
        if key in self.keys:
            self.keys[ key ].stop( self.context, self.player )

    def on_press ( self, key : KeyStroke ):
        key_stroke : KeyStroke = KeyStroke.parse( key ) if Value.typeof( key ) == str else key

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_press( self.context, self.player )

    def on_release ( self, key : Union[str, KeyStroke] ):
        key_stroke : KeyStroke = KeyStroke.parse( key ) if Value.typeof( key ) == str else key

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_release( self.context, self.player )

    def close ( self, closing : bool = False ):
        self.stop_all()

        if not closing:
            keyboard : KeyboardLibrary = self.context.library( KeyboardLibrary )

            keyboard.close( self )

class Grid:
    def __init__ ( self, keyboard : Keyboard, num : int = 1, den : int = 1 ):
        self.keyboard : Keyboard = keyboard
        self.length : Fraction = Fraction( num, den )
        self.start : int = self.keyboard.player.get_time()

    def get_delta ( self, context : Context, time : int ) -> int:
        length = context.voice.get_duration( float( self.length ) )

        rest = ( time - self.start ) % length

        if rest == 0:
            return 0
        
        return length - rest

    def reset ( self ):
        self.start = self.keyboard.player.get_time()

    def align ( self, context : Context, music : Music ) -> Music:
        return music.map( lambda e, i, s: e.clone( timestamp = self.get_delta( context, s ) + e.timestamp ).join( context ) )

def grid_create ( keyboard : Keyboard, num : int = 1, den : int = 1 ) -> Grid:
    return Grid( keyboard, num, den )

def grid_reset ( grid : Grid ) -> Grid:
    grid.reset()

def grid_align ( context : Context, grid : Grid, music : Music ) -> Music:
    return grid.align( context, music )

def register_key ( context : Context, keyboard : Keyboard, key : Node, expression : Node, toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None ):
    return keyboard.register_key( context, key, expression, toggle, hold, repeat, extend )

def push_flags ( context : Context, keyboard : Keyboard, *flags : Node ):
    return keyboard.push_flags( context, *flags )

def pop_flags ( context : Context, keyboard : Keyboard, *flags : Node ):
    return keyboard.pop_flags( context, *flags )

def push_prefix ( context : Context, keyboard : Keyboard, expression : Node ):
    return keyboard.push_prefix( context, expression )

def pop_prefix ( context : Context, keyboard : Keyboard ):
    return keyboard.pop_prefix( context )

def register_key_toggle ( context : Context, keyboard : Keyboard, key : Node, expression : Node ):
    return keyboard.register_key_toggle( context, key, expression )

def register_key_hold ( context : Context, keyboard : Keyboard, key : Node, expression : Node ):
    return keyboard.register_key_hold( context, key, expression )

def start ( context : Context, keyboard : Keyboard, key : Union[str, KeyStroke] ):
    return keyboard.start( key )

def stop ( context : Context, keyboard : Keyboard, key : Union[str, KeyStroke] ):
    return keyboard.stop( key )

def start_all ( context : Context, keyboard : Keyboard ):
    return keyboard.start_all()

def stop_all ( context : Context, keyboard : Keyboard ):
    return keyboard.stop_all()

def on_press ( context : Context, keyboard : Keyboard, key : Union[str, KeyStroke] ):
    return keyboard.on_press( key )

def on_release ( context : Context, keyboard : Keyboard, key : Union[str, KeyStroke] ):
    return keyboard.on_release( key )

def keyboard_create ( context : Context ) -> Keyboard:
    lib : KeyboardLibrary = context.library( KeyboardLibrary )

    return lib.create()

def keyboard_close ( context : Context, keyboard : Keyboard ):
    if keyboard != None:
        keyboard.close()
    else:
        lib : KeyboardLibrary = context.library( KeyboardLibrary )

        lib.close()

class KeyboardLibrary(Library):
    def __init__ ( self, player : MidiPlayer ):
        super().__init__( "keyboard" )

        self.player : MidiPlayer = player
    
    def on_link ( self ):
        self.assign_internal( "keyboards", list() )

        self.assign( "create", CallablePythonValue( keyboard_create ) )
        self.assign( "push_flags", CallablePythonValue( push_flags ) )
        self.assign( "pop_flags", CallablePythonValue( pop_flags ) )
        self.assign( "push_prefix", CallablePythonValue( push_prefix ) )
        self.assign( "pop_prefix", CallablePythonValue( pop_prefix ) )
        self.assign( "register", CallablePythonValue( register_key ) )
        self.assign( "register_hold", CallablePythonValue( register_key_hold ) )
        self.assign( "register_toggle", CallablePythonValue( register_key_toggle ) )
        self.assign( "on_press", CallablePythonValue( on_press ) )
        self.assign( "on_release", CallablePythonValue( on_release ) )
        self.assign( "start", CallablePythonValue( start ) )
        self.assign( "stop", CallablePythonValue( stop ) )
        self.assign( "start_all", CallablePythonValue( start_all ) )
        self.assign( "stop_all", CallablePythonValue( stop_all ) )
        self.assign( "close", CallablePythonValue( keyboard_close ) )

        self.assign( "grid\\create", CallablePythonValue( grid_create ) )
        self.assign( "grid\\reset", CallablePythonValue( grid_reset ) )
        self.assign( "grid\\align", CallablePythonValue( grid_align ) )
    
    @property
    def keyboards ( self ) -> List[Keyboard]:
        return self.lookup_internal( "keyboards" )

    @property
    def keys ( self ) -> Iterator[Tuple[KeyStroke, KeyAction]]:
        for kb in self.keyboards:
            for key, action in kb.keys.items():
                yield key, action

    @property
    def actions ( self ) -> Iterator[KeyAction]:
        return ( action for key, action in self.keys() )

    @property
    def pressed ( self ) -> Iterator[KeyAction]:
        return ( action for action in self.actions if action.is_active )

    @property
    def pressed_keys ( self ) -> Iterator[KeyStroke]:
        return ( action.key for action in self.pressed )
    
    @property
    def has_keys ( self ) -> Iterator[KeyAction]:
        iter = self.keys

        has_keys = next( self.keys, None ) != None

        if hasattr( iter, 'close' ):
            iter.close()

        return has_keys

    def create ( self ) -> Keyboard:
        keyboard = Keyboard( self.context, self.player )

        self.keyboards.append( keyboard )

        return keyboard
    
    def close ( self, keyboard : Optional[Keyboard] = None ):
        self.lookup_internal( "keyboards" )

        if keyboard != None:
            self.keyboards.remove( keyboard )
        else:
            for kb in self.keyboards: 
                kb.close( self.context, closing = True )
        
            self.keyboards.clear()

        if not self.has_keys:
            close_future : Future = self.lookup_internal( "close_future" )
            
            if close_future != None:
                close_future.set_result( None )

    def start ( self, key : KeyStroke ):
        for kb in self.keyboards:
            kb.start( key )
        
    def stop ( self, key : KeyStroke ):
        for kb in self.keyboards:
            kb.stop( key )

    def start_all ( self ):
        for kb in self.keyboards:
            kb.start_all()
        
    def stop_all ( self ):
        for kb in self.keyboards:
            kb.stop_all()

    def on_press ( self, key : KeyStroke ):
        for kb in self.keyboards:
            kb.on_press( key )

    def on_release ( self, key : KeyStroke ):
        for kb in self.keyboards:
            kb.on_release( key )

    async def join_async ( self ):
        close_future : Future = self.lookup_internal( "close_future" )

        if close_future == None:
            close_future = Future()

            self.assign_internal( "close_future", close_future )
        
        await close_future
