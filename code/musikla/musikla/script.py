from musikla.libraries.keyboard_pynput import KeyboardPynputLibrary
from musikla.libraries.keyboard_mido import KeyboardMidoLibrary
from musikla.core import Context, Library, Music, Value
from musikla.parser import Parser, Node
from musikla.audio import Player, InteractivePlayer
from musikla.audio.sequencers import FluidSynthSequencerFactory, ABCSequencerFactory, PDFSequencerFactory, HTMLSequencerFactory, MidiSequencerFactory, DebugSequencerFactory
from musikla.libraries import StandardLibrary, MusicLibrary, KeyboardLibrary, MidiLibrary
from typing import Optional, Union, Set, Dict, Any, cast
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

class Script:
    def __init__ ( self, code : Union[str, Node] = None, context : Context = Context.create(), config : ConfigParser = None ):
        self.context : Context = context
        self.parser : Parser = Parser()
        self.player : Player = Player()
        self.config : ConfigParser = config or load_config()
        self.tasks : Set[asyncio.Task] = set()
        self.soundfont : Optional[str] = None
        
        self.context.symbols.assign( 'script', self, local = True )
        
        self.libraries : Dict[str, Any] = {}
        
        self.add_sequencer_factory( ABCSequencerFactory )
        self.add_sequencer_factory( PDFSequencerFactory )
        self.add_sequencer_factory( HTMLSequencerFactory )
        self.add_sequencer_factory( MidiSequencerFactory )
        self.add_sequencer_factory( DebugSequencerFactory )
        self.add_sequencer_factory( FluidSynthSequencerFactory )

        # Import the builtin libraries
        self.import_library( StandardLibrary, self.player, prelude = True )
        self.import_library( MusicLibrary )
        self.import_library( KeyboardLibrary, self.player )
        self.import_library( KeyboardPynputLibrary )
        self.import_library( KeyboardMidoLibrary )
        self.import_library( MidiLibrary )

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

    def import_library ( self, library : Union[str, Path, Library, Any], *args : Any, context : Context = None, prelude : bool = False ):
        if type( library ) is str or isinstance( library, Path ):
            library_str = str( library )
                
            if library_str in self.libraries:
                lib_instance = cast( Library, self.libraries[ library_str ]( *args ) )

                self.context.link( lib_instance, self )
            elif library_str.lower().endswith( '.mkl' ):
                sub_context = self.create_subcontext( context, True, __main__ = False )

                self.execute_file( library_str, context = sub_context, fork = False, silent = True )

                context.symbols.import_from( sub_context.symbols, local = True )
            else:
                raise Exception( f'Trying to import library {library_str} not found.' )
        elif isinstance( library, Library ):
            self.context.link( library, self )
        elif issubclass( library, Library ):
            self.context.link( library( *args ), self )
        else:
            raise Exception( f'Trying to import library {library} not found.' )

    def parse ( self, code : str ) -> Node:
        return self.parser.parse( code )

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

    def eval ( self, code : Union[str, Node], context : Context = None, fork : bool = True, locals : Dict[str, Any] = {} ) -> Any:
        if type( code ) is str:
            code = self.parse( code )

        if context is None:
            context = self.create_subcontext( None, fork, **locals )
        elif locals:
            context = self.create_subcontext( context, fork, **locals )

        return Value.eval( context, code )
    
    def execute ( self, code : Union[str, Node], context : Context = None, fork : bool = True, silent : bool = False, sync : bool = False, realtime : bool = True ):
        value = self.eval( code, context = context, fork = fork )

        if not silent and value and isinstance( value, Music ):
            return self.play( value, sync = sync, realtime = realtime )

        return None
    
    def execute_file ( self, file : str, context : Context = None, fork : bool = True, silent : bool = False, sync : bool = False, realtime : bool = True, locals : Dict[str, Any] = {} ):
        code = self.parser.parse_file( file )
        
        absolute_file : str = os.path.abspath( file )

        value = self.eval( code, context = context, fork = fork, locals = {
            '__file__': absolute_file,
            '__dir__': str( Path( absolute_file ).parent ),
            **locals
        } )
        
        if not silent and value and isinstance( value, Music ):
            return self.play( value, sync = sync, realtime = realtime )

        return None

    async def join ( self ):
        for task in list( self.tasks ):
            await task

        self.player.sequencers[ 0 ].join()
