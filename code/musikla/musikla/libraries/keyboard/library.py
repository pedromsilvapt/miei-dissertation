from musikla.libraries.keyboard.buffer import KeyboardBuffer
from musikla.libraries.keyboard.virtual_player import VirtualPlayer
from musikla.core import Context, Library, Music, Value
from musikla.audio import Player
from musikla.core.callable_python_value import CallablePythonValue
from typing import Dict, List, Set, Type, Union, Optional, Iterator, Tuple, Any, cast
from musikla.parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, create_task
from io import FileIO
from pathlib import Path
from .grid import Grid
from .keyboard import Keyboard
from .event import EventSource, KeyEvent, KeyStroke, KeyStrokePress, KeyStrokeRelease, KeyboardEvent, MouseClick, MouseMove, MouseScroll, PianoKey
from .action import KeyAction

def register_key ( context : Context, keyboard : Keyboard, key : Node, expression : Node, args : List[str] = [], toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None, release : Node = None ):
    return keyboard.register_key( context, key, expression, args, toggle, hold, repeat, extend, release )

def push_flags ( context : Context, keyboard : Keyboard, *flags : Node ):
    return keyboard.push_flags( context, *flags )

def pop_flags ( context : Context, keyboard : Keyboard, *flags : Node ):
    return keyboard.pop_flags( context, *flags )

def push_prefix ( context : Context, keyboard : Keyboard, expression : Node ):
    return keyboard.push_prefix( context, expression )

def pop_prefix ( context : Context, keyboard : Keyboard ):
    return keyboard.pop_prefix( context )

def start ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.start( key )

def stop ( context : Context, keyboard : Keyboard, key : Union[str, KeyboardEvent] ):
    return keyboard.stop( key )

def start_all ( context : Context, keyboard : Keyboard ):
    return keyboard.start_all()

def stop_all ( context : Context, keyboard : Keyboard ):
    return keyboard.stop_all()

def on_press ( context : Context, key : Union[str, KeyboardEvent] ):
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    return lib.on_press( key )

def on_release ( context : Context, key : Union[str, KeyboardEvent] ):
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    return lib.on_release( key )

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

def keyboard_open_repl ( context : Context ):
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    lib.eval( context )

    return None

def keyboard_readperf ( context : Context, file : str, keyboards : List[Keyboard] = None ) -> Music:
    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    return lib.readperf( context, file, keyboards )

def keyboard_filedialog ( context : Context, title : str = "File", text : str = "File Path:", default_value : str = None, cb = None ):
    from prompt_toolkit.patch_stdout import patch_stdout
    from prompt_toolkit.shortcuts import input_dialog
    from prompt_toolkit.completion import PathCompleter

    lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

    def _run ():
        with patch_stdout():
            application = input_dialog( title = title, text = text, completer = PathCompleter() )

            with application.input.raw_mode():
                application.input.read_keys()

            application.layout.current_control.buffer.insert_text(default_value or "")
            
            return application.run_async()

    lib.prompt( _run, cb )

class KeyboardLibrary(Library):
    def __init__ ( self, player : Player ):
        super().__init__( "keyboard" )

        self.player : Player = player
        self.paused : bool = False
    
    def on_link ( self, script ):
        self.assign_internal( "keyboards", list() )
        self.assign_internal( "event_sources", list() )
        self.assign_internal( "event_types", dict() )
        
        self.assign( "create", CallablePythonValue( keyboard_create ) )
        self.assign( "push_flags", CallablePythonValue( push_flags ) )
        self.assign( "pop_flags", CallablePythonValue( pop_flags ) )
        self.assign( "push_prefix", CallablePythonValue( push_prefix ) )
        self.assign( "pop_prefix", CallablePythonValue( pop_prefix ) )
        self.assign( "register", CallablePythonValue( register_key ) )
        self.assign( "on_press", CallablePythonValue( on_press ) )
        self.assign( "on_release", CallablePythonValue( on_release ) )
        self.assign( "start", CallablePythonValue( start ) )
        self.assign( "stop", CallablePythonValue( stop ) )
        self.assign( "start_all", CallablePythonValue( start_all ) )
        self.assign( "stop_all", CallablePythonValue( stop_all ) )
        self.assign( "close", CallablePythonValue( keyboard_close ) )

        self.assign( "record", CallablePythonValue( keyboard_record ) )
        self.assign( "readperf", CallablePythonValue( keyboard_readperf ) )
        self.assign( "replay", CallablePythonValue( keyboard_replay ) )
        self.assign( "open_repl", CallablePythonValue( keyboard_open_repl ) )
        self.assign( "filedialog", CallablePythonValue( keyboard_filedialog ) )

        self.assign( "Grid", Grid )
        self.assign( "Buffer", KeyboardBuffer )

        self.assign( "KeyEvent", KeyEvent )
        self.assign( "KeyStroke", KeyStroke )
        self.assign( "KeyStrokePress", KeyStrokePress )
        self.assign( "KeyStrokeRelease", KeyStrokeRelease )
        self.assign( "PianoKey", PianoKey )
        self.assign( "MouseClick", MouseClick )
        self.assign( "MouseMove", MouseMove )
        self.assign( "MouseScroll", MouseScroll )

        self.register_event_type(
            PianoKey, KeyStroke, MouseClick, MouseMove, MouseScroll
        )

        script.import_module( self.context, Path( __file__ ).parent / "library.mkl", save_cache = False )
        
    def register_event_type ( self, *events : Type[KeyboardEvent] ):
        for event in events:
            self.event_types[ event.__name__ ] = event

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
    def event_types ( self ) -> Dict[str, Type[KeyboardEvent]]:
        return self.lookup_internal( 'event_types' )

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
        keyboard = Keyboard( self.context )

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

    def on_press ( self, key : Union[str, KeyboardEvent] ):
        if self.paused: return

        key = Keyboard.as_event( key )

        if any( key in kb for kb in self.keyboards ):
            self._record_key( 'press', key )

        for kb in self.keyboards:
            kb.on_press( key )

    def on_release ( self, key : Union[str, KeyboardEvent] ):
        if self.paused: return

        key = Keyboard.as_event( key )

        if any( key in kb for kb in self.keyboards ):
            self._record_key( 'release', key )
        
        for kb in self.keyboards:
            kb.on_release( key )

    async def prompt_async ( self, prompt, cb = None ):
        self.paused = True

        try:
            res = await prompt()

            if callable( cb ): cb( res )

            return res
        finally:
            self.paused = False
        
    def prompt ( self, prompt, cb = None ):
        create_task( self.prompt_async( prompt, cb = cb ) )

    async def eval_async ( self, context : Context ):
        from .prompt import run_async

        await self.prompt_async( lambda: run_async( context, self.player ) )

    def eval ( self, context : Context ):
        create_task( self.eval_async( context ) )
        
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

    def _serialize_event ( self, key : KeyboardEvent ):
        import json

        parameters = key.get_parameters()

        return ( key.__class__.__name__, key.serialize(), json.dumps( parameters, separators=(',', ':') ) if parameters else "" )

    def _deserialize_event ( self, class_name : str, event : str, parameters : str ) -> KeyboardEvent:
        import json

        if class_name in self.event_types:
            return self.event_types[ class_name ].deserialize( event, json.loads( parameters ) if parameters else {} )
        else:
            raise BaseException( f"Could not find event { class_name }" )

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

            if kind == 'press' and ( key_str not in pressed or not key.binary ):
                pressed.add( key_str )
            elif kind == 'release' and key_str in pressed:
                pressed.remove( key_str )
            else:
                return
            
            time = self.player.get_time() - self.record_start

            class_name, data, parameters = self._serialize_event( key )

            fd.write( f'{time},{kind},{class_name},{data},{parameters}\n' )

            fd.flush()

    def record ( self, file : str ):
        self.assign_internal( 'record_file', file )

    def readperf ( self, context : Context, file : str, keyboards : List[Keyboard] = None ) -> Music:
        with open( file, 'r' ) as f:
            entries = [ line.strip().split( ',' ) for line in list( f ) ]

        player = VirtualPlayer()

        for time, kind, class_name, data, parameters in entries:
            time = int( time )
            
            key : KeyboardEvent = self._deserialize_event( class_name, data, parameters )

            if kind == 'press':
                player.on_press( time, key )
            elif kind == 'release':
                player.on_release( time, key )
        
        if keyboards is None:
            return player.generate( context, self.keyboards )
        else:
            return player.generate( context, keyboards )

    def replay ( self, file : str, delay : int = 0 ):
        async def _replay ():
            with open( file, 'r' ) as f:
                entries = [ line.strip().split( ',' ) for line in list( f ) ]

            start = self.player.get_time()

            if delay > 0:
                await sleep( delay / 1000.0 )

            for time, kind, class_name, data, parameters in entries:
                time = int( time )
                
                key : KeyboardEvent = self._deserialize_event( class_name, data, parameters )

                await sleep( ( time - start ) / 1000.0 )

                start = time

                if kind == 'press':
                    self.on_press( key )
                elif kind == 'release':
                    self.on_release( key )

        create_task( _replay() )

    async def join_async ( self ):
        close_future : Future = self.lookup_internal( "close_future" )

        if close_future == None:
            close_future = Future()

            self.assign_internal( "close_future", close_future )

        await close_future
