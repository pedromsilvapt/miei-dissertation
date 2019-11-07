import sys
import asyncio
import argparse
from pathlib import Path

from audio import MidiPlayer, AsyncMidiPlayer
from audio.sequencers import FluidSynthSequencer, ABCSequencer
from core import Context, Value
from parser import Parser
from libraries import KeyboardLibrary, KeyStroke, StandardLibrary, MusicLibrary

from pynput import keyboard
from typing import List

class CliApplication:
    def __init__ ( self, argv,  ):
        self.argv = argv
        self.builtin_libraries = {
            'std': StandardLibrary,
            'keyboard': KeyboardLibrary,
            'music': MusicLibrary
        }
        self.parser = Parser()
        self.keyboard_state = dict()
        self.player = None

    def create_context ( self ):
        return Context.create()

    def import_library ( self, context : Context, library : str, *args ):
        if library.lower() in self.builtin_libraries:
            instance = self.builtin_libraries[ library.lower() ]( *args )

            context.link( instance )
        else:
            ast = self.parser.parse_file( library )

            ast.eval( context )

    def eval ( self, context, ast ):
        value = ast.eval( context )

        if value and value.is_music:
            self.player.play_more( value )

    def get_key_info ( self, key : keyboard.Key ) -> (bool, str):
        key_str = str( key )
        key_str = key_str[ len( 'Key.' ): ] if key_str.startswith( 'Key.' ) else key_str[ 1:-1 ]

        is_modifier : bool = key_str in [ 'ctrl', 'alt', 'shift' ]
        
        return ( is_modifier, key_str )

    def get_keystrokes ( self, is_modifier : bool, key : str ) -> List[KeyStroke]:
        keystrokes : List[KeyStroke] = []

        ctrl = 'ctrl' in self.keyboard_state
        alt = 'alt' in self.keyboard_state
        shift = 'shift' in self.keyboard_state

        if is_modifier:
            for key in self.keyboard_state.keys():
                if key not in [ 'ctrl', 'alt', 'shift' ]:
                    keystrokes.append( KeyStroke( ctrl, alt, shift, key ) )
        else:
            keystrokes.append( KeyStroke( ctrl, alt, shift, key ) )

        return keystrokes
            

    def keyboard_on_press ( self, virtual_keyboard : KeyboardLibrary, key : keyboard.Key ):
        ( is_modifier, key ) = self.get_key_info( key )

        self.keyboard_state[ key ] = True

        keystrokes = self.get_keystrokes( is_modifier, key )
            
        for keystroke in keystrokes:
            if keystroke == KeyStroke( True, True, True, 'c' ):
                raise KeyboardInterrupt()
            
            virtual_keyboard.on_press( keystroke )

    def keyboard_on_release ( self, virtual_keyboard : KeyboardLibrary, key : keyboard.Key ):
        ( is_modifier, key ) = self.get_key_info( key )

        keystrokes = self.get_keystrokes( is_modifier, key )

        if key in self.keyboard_state:
            del self.keyboard_state[ key ]

        for keystroke in keystrokes:
            virtual_keyboard.on_release( keystroke )


    async def keyboard ( self, context : Context, virtual_keyboard : KeyboardLibrary ):
        print( "Keyboard active." )

        loop = asyncio.get_running_loop()

        with keyboard.Listener(
                on_press = lambda key: loop.call_soon_threadsafe( self.keyboard_on_press, virtual_keyboard, key ),
                on_release = lambda key: loop.call_soon_threadsafe( self.keyboard_on_release, virtual_keyboard, key ),
                suppress = False
            ) as listener:

            await virtual_keyboard.join_async()

    async def run ( self ):
        parser = argparse.ArgumentParser( description = 'Evaluate musical expression' )

        parser.add_argument( 'file', type = str, nargs = '?', help = 'Files to evaluate. No file means the input will be read from the stdin' )
        parser.add_argument( '-i', '--import', dest = 'imports', action = 'append', type = str, help = 'Import an additional library. These can be builtin libraries, or path to .ml and .py files' )
        parser.add_argument( '-o', '--output', dest = 'outputs', type = str, action = 'append', help = 'Where to output to. By default outputs the sounds to the device\'s speakers.' )
        parser.add_argument( '--soundfont', type = str, help = 'Use a custom soundfont .sf2 file' )
        
        options = parser.parse_args( self.argv )

        self.player = MidiPlayer()

        for output in options.outputs or [ 'pulseaudio' ]:
            suffix = ( Path( output ).suffix or '' ).lower()

            if suffix == '.abc':
                self.player.sequencers.append( ABCSequencer( output ) )
            else:
                self.player.sequencers.append( FluidSynthSequencer( output, options.soundfont ) )

        if options.soundfont != None:
            self.player.soundfont = options.soundfont

        context = self.create_context()

        # Always import the std library
        self.import_library( context, 'std' )
        self.import_library( context, 'music' )
        self.import_library( context, 'keyboard', self.player )

        for lib in options.imports or []:
            self.import_library( context, lib )

        try:
            if options.file == None:
                # Super duper naive repl that accepts only a sequence of one-liners
                for line in sys.stdin:
                    ast = self.parser.parse( line )

                    self.eval( context, ast )
            else:
                ast = self.parser.parse_file( options.file )

                async_player = AsyncMidiPlayer( lambda: ast.eval( context ), self.player )

                await async_player.start()

            keyboard : KeyboardLibrary = context.library( KeyboardLibrary )

            if keyboard != None and len( keyboard.registered ) > 0:
                await self.keyboard( context, keyboard )
            else:
                # Wait for the end of the player if there is anything left to play
                self.player.join()
        finally:
            self.player.close()
