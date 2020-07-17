from musikla.libraries.keyboard_pynput import KeyboardPynputLibrary
from musikla.libraries.keyboard_mido import KeyboardMidoLibrary
from musikla.core import Context, Library, Music, Value
from musikla.parser import Parser, Node, ParserError, MusiklaExecutionError
from musikla.audio import Player, InteractivePlayer
from musikla.audio.sequencers import FluidSynthSequencerFactory, ABCSequencerFactory, PDFSequencerFactory, HTMLSequencerFactory, MidiSequencerFactory, DebugSequencerFactory
from musikla.libraries import StandardLibrary, MusicLibrary, KeyboardLibrary, MidiLibrary
from typing import Optional, Tuple, Union, Set, Dict, List, Any, cast
from pathlib import Path
from configparser import ConfigParser
import asyncio
import os

def load_config () -> ConfigParser:
    config_path = Path.home() / 'musikla.ini'

    config = ConfigParser()

    if os.path.isfile( config_path ):
        config.read( config_path )
    
    return config

def load_paths ( config : ConfigParser, section : str, option : str ) -> List[str]:
    paths_str = config.get( section, option, fallback = None )

    if paths_str is None:
        return []
    
    return paths_str.split( ":" )

class Script:
    def __init__ ( self, code : Union[str, Node] = None, context : Context = None, config : ConfigParser = None ):
        self.prelude_context : Context = context or Context.create()
        self.context : Context = self.prelude_context.fork( symbols = self.prelude_context.symbols.fork( True ) )
        self.parser : Parser = Parser()
        self.player : Player = Player()
        self.config : ConfigParser = config or load_config()
        self.tasks : Set[asyncio.Task] = set()
        self.soundfont : Optional[str] = None
        self.import_paths : List[str] = load_paths( self.config, "Musikla", "path" )
        self.import_cache : Dict[str, Context] = {}
        self.import_extensions : List[str] = [ '.py', '.mkl' ]
        self.files_cache : List[Tuple[str, str]] = []

        self.player.custom_error_printer = self.print_error

        self.prelude_context.symbols.assign( 'script', self, local = True )
        # Some core code may depend on the script variable to get a hold of it at runtime
        # But in some child context, the user might have locally binded a custom value to the symbol named "script"
        # And thus any services that were handed that child context would have difficulty finding the main script variable
        # Therefore we publish it too in the "internal" container, which is not available through the musikla language
        # And so we can ensure with more safety that it will be the correct script variable
        self.prelude_context.symbols.assign( 'script', self, local = True, container = 'internal' )

        # This context will be considered main for this execution
        # This allows scripts to detect when they are being imported (and should only declare symbols)
        # versus when they are being executed (and should setup keyboards/play stuff/etc...)
        self.context.symbols.assign( '__main__', True, local = True )

        self.libraries : Dict[str, Any] = {}
        
        self.add_sequencer_factory( ABCSequencerFactory )
        self.add_sequencer_factory( PDFSequencerFactory )
        self.add_sequencer_factory( HTMLSequencerFactory )
        self.add_sequencer_factory( MidiSequencerFactory )
        self.add_sequencer_factory( DebugSequencerFactory )
        self.add_sequencer_factory( FluidSynthSequencerFactory )

        # Import the builtin libraries
        self.import_library( StandardLibrary, self.player, context = self.prelude_context )
        self.import_library( MusicLibrary, context = self.prelude_context )
        self.import_library( KeyboardLibrary, self.player, context = self.prelude_context )
        self.import_library( KeyboardPynputLibrary, context = self.prelude_context )
        self.import_library( KeyboardMidoLibrary, context = self.prelude_context )
        self.import_library( MidiLibrary, context = self.prelude_context )

        for path in load_paths( self.config, 'Musikla', 'prelude' ):
            resolved_path = self.resolve_import( None, path, None )

            self.import_module( self.prelude_context, resolved_path )

        for path in load_paths( self.config, 'Musikla', 'autoload' ):
            resolved_path = self.resolve_import( None, path, None )

            self.import_module( self.context, resolved_path )

        if code != None:
            self.eval( code )
    
    def add_sequencer_factory ( self, factory : Any ):
        self.player.add_sequencer_factory( factory, self.context, self.config )

    def add_library ( self, *libraries : Any ):
        for library in libraries:
            name : str = library.__name__

            if name.endswith( 'Library' ):
                name = name[ :-7 ]

            self.libraries[ name.lower() ] = library

    def resolve_import ( self, current_path : Optional[str], import_path : str, local : Optional[bool] ) -> str:
        if local is True or local is None:
            if os.path.isabs( import_path ):
                return import_path
            
            if current_path is not None:
                joined_path = str( Path( current_path ).parent.joinpath( import_path ).resolve() )

                if os.path.exists( joined_path ):
                    return joined_path
                
                for ext in self.import_extensions:
                    if os.path.exists( joined_path + ext ):
                        return joined_path + ext

        if local is False or local is None:
            for path in self.import_paths:
                joined_path = str( Path( path ).joinpath( import_path ).resolve() )

                if any( joined_path.endswith( ext ) for ext in self.import_extensions ):
                    if os.path.exists( joined_path ):
                        return joined_path
                
                for ext in self.import_extensions:
                    if os.path.exists( joined_path + ext ):
                        return joined_path + ext

    def import_module ( self, context : Context, module_path : str, save_cache : bool = True ):
        module_path = os.path.realpath( module_path )

        if module_path not in self.import_cache:
            module_context : Context = self.create_subcontext( self.prelude_context, fork = True )

            self.execute_file( module_path, module_context, fork = False, silent = True )

            if save_cache:
                self.import_cache[ module_path ] = module_context
        else:
            module_context : Context = self.import_cache[ module_path ]

        if module_context is not None:
            context.symbols.import_from( module_context.symbols, local = True )

    def import_library ( self, library : Union[str, Library, Any], *args : Any, context : Context = None ):
        context = context or self.context

        if type( library ) is str:
            if library in self.libraries:
                lib_instance = cast( Library, self.libraries[ library ]( *args ) )

                context.link( lib_instance, self )
            else:
                raise Exception( f'Trying to import library {library} not found.' )
        elif isinstance( library, Library ):
            context.link( library, self )
        elif issubclass( library, Library ):
            context.link( library( *args ), self )
        else:
            raise Exception( f'Trying to import library {library} not found.' )

    def parse ( self, code : str, rule : str = None ) -> Node:
        return self.parser.parse( code, rule = rule )

    def play ( self, music : Music, sync : bool = True, realtime = True ) -> Optional[asyncio.Task]:
        if sync:
            self.player.play_more( music )

            self.player.join()
        else:
            # TODO Instead of music, it should eval the thing
            async_player = InteractivePlayer( lambda: list( music ), self.player, realtime = realtime )

            task = asyncio.create_task( async_player.start() )

            self.tasks.add( task )

            task.add_done_callback( lambda a: self.tasks.remove( task ) )

            return task
    
    def create_subcontext ( self, context = None, fork : bool = True, **kargs ) -> Context:
        context = ( context or self.context )
        
        if fork:
            context = context.fork( symbols = context.symbols.fork() )

        for key, value in kargs.items():
            context.symbols.assign( key, value, local = True )

        return context

    def eval ( self, code : Union[str, Node], context : Context = None, fork : bool = False, locals : Dict[str, Any] = {} ) -> Any:
        try:
            if type( code ) is str:
                code = self.parse( code )

            if context is None:
                context = self.create_subcontext( None, fork = fork, **locals )
            elif locals:
                context = self.create_subcontext( context, fork = fork, **locals )

            return Value.eval( context, code )
        except BaseException as err:
            self.print_error( err )
    
    def execute ( self, code : Union[str, Node], context : Context = None, fork : bool = False, silent : bool = False, sync : bool = False, realtime : bool = True ):
        try:
            value = self.eval( code, context = context, fork = fork )

            if value and isinstance( value, Music ):
                if not silent:
                    return self.play( value, sync = sync, realtime = realtime )
                else:
                    # Since code can be lazy, we need to make sure we actually execute the file even
                    # when we have no intention of handling it's events
                    for _ in value.expand( context ): pass

            return None
        except BaseException as err:
            self.print_error( err )
    
    def print_error ( self, err : BaseException ):
        if isinstance( err, ParserError ):
            print( err )
        elif isinstance( err, MusiklaExecutionError ):
            file : Optional[str] = None
            contents : Optional[str] = None

            if err.reporter is None and err.position is not None and err.position[ 0 ] >= 0 and err.position[ 0 ] < len( self.files_cache ):
                file, contents = self.files_cache[ err.position[ 0 ] ]

                err.create_reporter( file, contents )

            print( err )
        else:
            print( str( err ) )

    def execute_file ( self, file : str, context : Context = None, fork : bool = False, silent : bool = False, sync : bool = False, realtime : bool = True, locals : Dict[str, Any] = {} ):
        try:
            with open( file, 'r', encoding="utf-8" ) as f:
                file_id = len( self.files_cache )

                file_contents = f.read()

                self.files_cache.append( ( file, file_contents ) )

                code = self.parser.parse( file_contents, file = file, file_id = file_id )
            
            absolute_file : str = os.path.abspath( file )

            value = self.eval( code, context = context, fork = fork, locals = {
                '__file__': absolute_file,
                '__dir__': str( Path( absolute_file ).parent ),
                **locals
            } )
            
            if value and isinstance( value, Music ):
                if not silent:
                    return self.play( value, sync = sync, realtime = realtime )
                else:
                    # Since code can be lazy, we need to make sure we actually execute the file even
                    # when we have no intention of handling it's events
                    for _ in value.expand( context ): pass
        except BaseException as err:
            self.print_error( err )

        return None

    async def join ( self ):
        for task in list( self.tasks ):
            await task

        self.player.sequencers[ 0 ].join()
