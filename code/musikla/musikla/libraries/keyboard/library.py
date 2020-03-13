from musikla.core import Context, Library, Music
from musikla.audio import Player
from musikla.core.callable_python_value import CallablePythonValue
from typing import List, Set, Union, Optional, Iterator, Tuple, Any, cast
from musikla.parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, FIRST_COMPLETED, create_task
from io import FileIO
from .grid import Grid
from .keyboard import Keyboard
from .event import EventSource, KeyboardEvent, MouseClick, MouseMove, MouseScroll
from .action import KeyAction

def grid_create ( keyboard : Keyboard, num : int = 1, den : int = 1 ) -> Grid:
    return Grid( keyboard, num, den )

def grid_reset ( grid : Grid ) -> Grid:
    grid.reset()

    return grid

def grid_align ( context : Context, grid : Grid, music : Music ) -> Music:
    return grid.align( context, music )

def register_key ( context : Context, keyboard : Keyboard, key : Node, expression : Node, args : List[str] = [], toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None ):
    return keyboard.register_key( context, key, expression, args, toggle, hold, repeat, extend )

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

def start ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.start( key )

def stop ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.stop( key )

def start_all ( context : Context, keyboard : Keyboard ):
    return keyboard.start_all()

def stop_all ( context : Context, keyboard : Keyboard ):
    return keyboard.stop_all()

def on_press ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.on_press( key )

def on_release ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.on_release( key )

def keyboard_create ( context : Context ) -> Keyboard:
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    return lib.create()

def keyboard_close ( context : Context, keyboard : Keyboard ):
    if keyboard != None:
        keyboard.close()
    else:
        lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

        lib.close()

def keyboard_record ( context : Context, file : str ):
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    lib.record( file )

def keyboard_replay ( context : Context, file : str ):
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    lib.replay( file )

class KeyboardLibrary(Library):
    def __init__ ( self, player : Player ):
        super().__init__( "keyboard" )

        self.player : Player = player
    
    def on_link ( self ):
        self.assign_internal( "keyboards", list() )
        self.assign_internal( "event_sources", list() )

        self.assign( "create", CallablePythonValue( keyboard_create ) )
        self.assign( "push_flags", CallablePythonValue( push_flags ) )
        self.assign( "pop_flags", CallablePythonValue( pop_flags ) )
        self.assign( "push_prefix", CallablePythonValue( push_prefix ) )
        self.assign( "pop_prefix", CallablePythonValue( pop_prefix ) )
        self.assign( "register", CallablePythonValue( register_key ) )
        # self.assign( "register_hold", CallablePythonValue( register_key_hold ) )
        # self.assign( "register_toggle", CallablePythonValue( register_key_toggle ) )
        self.assign( "on_press", CallablePythonValue( on_press ) )
        self.assign( "on_release", CallablePythonValue( on_release ) )
        self.assign( "start", CallablePythonValue( start ) )
        self.assign( "stop", CallablePythonValue( stop ) )
        self.assign( "start_all", CallablePythonValue( start_all ) )
        self.assign( "stop_all", CallablePythonValue( stop_all ) )
        self.assign( "close", CallablePythonValue( keyboard_close ) )

        self.assign( "record", CallablePythonValue( keyboard_record ) )
        self.assign( "replay", CallablePythonValue( keyboard_replay ) )

        self.assign( "grid\\create", CallablePythonValue( grid_create ) )
        self.assign( "grid\\reset", CallablePythonValue( grid_reset ) )
        self.assign( "grid\\align", CallablePythonValue( grid_align ) )

        self.assign( "MouseClick", MouseClick )
        self.assign( "MouseMove", MouseMove )
        self.assign( "MouseScroll", MouseScroll )
    
    @property
    def keyboards ( self ) -> List[Keyboard]:
        return self.lookup_internal( "keyboards" )

    @property
    def record_file ( self ) -> str:
        return self.lookup_internal( 'record_file' )
    
    @property
    def record_fd ( self ) -> FileIO:
        return self.lookup_internal( 'record_fd' )
        
    @property
    def record_start ( self ) -> int:
        return self.lookup_internal( 'record_start' )

    @property
    def event_sources ( self ) -> List[EventSource]:
        return self.lookup_internal( 'event_sources' )

    @property
    def keys ( self ) -> Iterator[Tuple[KeyboardEvent, KeyAction]]:
        for kb in self.keyboards:
            for key, action in kb.keys.items():
                yield key, action

    @property
    def actions ( self ) -> Iterator[KeyAction]:
        return ( action for key, action in self.keys )

    @property
    def pressed ( self ) -> Iterator[KeyAction]:
        return ( action for action in self.actions if action.is_active )

    @property
    def pressed_keys ( self ) -> Iterator[KeyboardEvent]:
        return ( action.key for action in self.pressed )
    
    @property
    def has_keys ( self ) -> bool:
        iter = self.keys

        has_keys = next( self.keys, None ) != None

        if hasattr( iter, 'close' ):
            cast( Any, iter ).close()

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
                kb.close( closing = True )
        
            self.keyboards.clear()

            fd = self.record_fd

            if fd is not None:
                fd.close()

        if not self.has_keys:
            close_future : Future = self.lookup_internal( "close_future" )
            
            if close_future != None:
                close_future.set_result( None )

    def start ( self, key : KeyboardEvent ):
        for kb in self.keyboards:
            kb.start( key )
        
    def stop ( self, key : KeyboardEvent ):
        for kb in self.keyboards:
            kb.stop( key )

    def start_all ( self ):
        for kb in self.keyboards:
            kb.start_all()
        
    def stop_all ( self ):
        for kb in self.keyboards:
            kb.stop_all()

    def on_press ( self, key : KeyboardEvent ):
        self._record_key( 'press', key )

        for kb in self.keyboards:
            kb.on_press( key )

    def on_release ( self, key : KeyboardEvent ):
        self._record_key( 'release', key )
        
        for kb in self.keyboards:
            kb.on_release( key )

    def add_source ( self, source : EventSource ):
        self.event_sources.append( source )

    async def listen ( self ):
        try:
            for source in self.event_sources:
                source.listen()

            await self.join_async()
        finally:
            for source in self.event_sources:
                source.close()

    def _record_key ( self, kind : str, key : KeyboardEvent ):
        file = self.record_file

        if file is not None:
            fd = self.record_fd

            if fd is None:
                fd = open( file, 'w' )

                self.assign_internal( 'record_fd', fd )

                self.assign_internal( 'record_start', self.player.get_time() )

                self.assign_internal( 'record_pressed', set() )
            
            pressed : Set[str] = self.lookup_internal( 'record_pressed' )

            key_str = str( key )

            if kind == 'press' and key_str not in pressed:
                pressed.add( key_str )
            elif kind == 'release' and key_str in pressed:
                pressed.remove( key_str )
            else:
                return
            
            time = self.player.get_time() - self.record_start

            fd.write( f'{time},{kind},{str(key)}\n' )

            fd.flush()

    def record ( self, file : str ):
        self.assign_internal( 'record_file', file )

    def replay ( self, file : str, delay : int = 0 ):
        async def _replay ():
            with open( file, 'r' ) as f:
                entries = [ line.split( ',' ) for line in list( f ) ]

            start = self.player.get_time()

            if delay > 0:
                await sleep( delay / 1000.0 )

            for time, type, key in entries:
                time = int( time )
                
                await sleep( ( time - start ) / 1000.0 )

                start = time

                if type == 'press':
                    self.on_press( key )
                elif type == 'release':
                    self.on_release( key )


        create_task( _replay() )

    async def join_async ( self ):
        close_future : Future = self.lookup_internal( "close_future" )

        if close_future == None:
            close_future = Future()

            self.assign_internal( "close_future", close_future )

        await close_future
