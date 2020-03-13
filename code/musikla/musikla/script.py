from musikla.libraries.keyboard_pynput import KeyboardPynputLibrary
from musikla.libraries.keyboard_mido import KeyboardMidoLibrary
from musikla.core.music import MusicBuffer
from musikla.core import Context, Library, Music, Value
from musikla.parser import Parser, Node
from musikla.audio import Player, AsyncMidiPlayer
from musikla.audio.sequencers import Sequencer, SequencerFactory, FluidSynthSequencerFactory, ABCSequencerFactory
from musikla.libraries import StandardLibrary, MusicLibrary, KeyboardLibrary, MidiLibrary
from typing import Optional, Union, List, Set, Dict, Any, cast
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
        
        self.libraries : Dict[str, Any] = {}
        
        self.player.add_sequencer_factory( ABCSequencerFactory, self.context, self.config )
        self.player.add_sequencer_factory( FluidSynthSequencerFactory, self.context, self.config )

        # Import the builtin libraries
        self.import_library( StandardLibrary )
        self.import_library( MusicLibrary )
        self.import_library( KeyboardLibrary, self.player )
        self.import_library( KeyboardPynputLibrary )
        self.import_library( KeyboardMidoLibrary )
        self.import_library( MidiLibrary )

        if code != None:
            self.eval( code )
    
    def add_library ( self, *libraries : Any ):
        for library in libraries:
            name : str = library.__name__

            if name.endswith( 'Library' ):
                name = name[ :-7 ]

            self.libraries[ name.lower() ] = library

    def import_library ( self, library : Union[str, Library, Any], *args : Any ):
        if type( library ) is str:
            if library in self.libraries:
                lib_instance = cast( Library, self.libraries[ library ]( *args ) )

                self.context.link( lib_instance )
            elif library.lower().endswith( '.mkl' ):
                node = self.parser.parse_file( library )

                return self.eval( node )
            else:
                raise Exception( f'Trying to import library {library} not found.' )
        elif isinstance( library, Library ):
            self.context.link( library )
        elif issubclass( library, Library ):
            self.context.link( library( *args ) )
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
            async_player = AsyncMidiPlayer( lambda: list( music ), self.player, realtime = realtime )

            task = asyncio.create_task( async_player.start() )

            self.tasks.add( task )

            task.add_done_callback( lambda a: self.tasks.remove( task ) )

            return task
    
    def create_subcontext ( self, context = None, **kargs ) -> Context:
        context = ( context or self.context ).fork( symbols = self.context.symbols.fork() )

        for key, value in kargs.items():
            context.symbols.assign( key, value, local = True )

        return context

    def eval ( self, code : Union[str, Node], context : Context = None, locals : Dict[str, Any] = {} ) -> Any:
        if type( code ) is str:
            code = self.parse( code )

        if context is None:
            context = self.create_subcontext( **locals )
        elif locals:
            context = self.create_subcontext( context, **locals )

        return Value.eval( context, code )
    
    def execute ( self, code : Union[str, Node], context : Context = None, sync : bool = False, realtime : bool = True ):
        value = self.eval( code, context = context )

        if value and isinstance( value, Music ):
            return self.play( value, sync = sync, realtime = realtime )

        return None
    
    def execute_file ( self, file : str, context : Context = None, sync : bool = False, realtime : bool = True ):
        code = self.parser.parse_file( file )
        
        value = self.eval( code, context = context, locals = {
            __file__: file
        } )
        
        if value and isinstance( value, Music ):
            return self.play( value, sync = sync, realtime = realtime )

        return None

    async def join ( self ):
        for task in list( self.tasks ):
            await task

        self.player.sequencers[ 0 ].join()
