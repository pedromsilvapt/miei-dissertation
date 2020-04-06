import sys
import argparse
import os

from musikla.core import Context
from musikla.libraries import KeyboardLibrary, MidiLibrary
from musikla import Script
from typing import cast
from colorama import init

class CliApplication:
    default_output = 'pulseaudio' if os.name == 'posix' else 'dsound'

    def __init__ ( self, argv ):
        self.argv = argv

    def enable_echo(self, fd, enabled):
        if os.name == 'posix':
            import termios
            
            (iflag, oflag, cflag, lflag, ispeed, ospeed, cc) \
                = termios.tcgetattr(fd)

            if enabled:
                lflag |= termios.ECHO
            else:
                lflag &= ~termios.ECHO

            new_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
            termios.tcsetattr(fd, termios.TCSANOW, new_attr)

    async def keyboard ( self, context : Context, virtual_keyboard : KeyboardLibrary ):
        print( "Keyboard active." )

        try:
            self.enable_echo( sys.stdin.fileno(), False )

            await virtual_keyboard.listen()
        finally:
            self.enable_echo( sys.stdin.fileno(), True )

    async def run ( self ):
        init()
        
        parser = argparse.ArgumentParser( description = 'Evaluate musical expression' )

        parser.add_argument( 'file', type = str, nargs = '?', help = 'Files to evaluate. No file means the input will be read from the stdin' )
        parser.add_argument( '-i', '--import', dest = 'imports', action = 'append', type = str, help = 'Import an additional library. These can be builtin libraries, or path to .ml and .py files' )
        parser.add_argument( '-o', '--output', dest = 'outputs', type = str, action = 'append', help = 'Where to output to. By default outputs the sounds to the device\'s speakers.' )
        parser.add_argument( '--midi', type = str, help = 'Use a custom MIDI port by default when no name is specified' )
        parser.add_argument( '--soundfont', type = str, help = 'Use a custom soundfont .sf2 file' )
        parser.add_argument( '--print-events', dest = 'print_events', action='store_true', help = 'Print events (notes) to the console as they are played.' )
        
        options = parser.parse_args( self.argv )

        script = Script()

        script.player.print_events = bool( options.print_events )
        
        if not script.config.has_section( 'Musikla' ):
            script.config.add_section( 'Musikla' )

        if options.soundfont != None:
            script.config.set( 'Musikla', 'soundfont', options.soundfont )

        if options.midi != None:
            script.config.set( 'Musikla', 'midi_input', options.midi )

        # if options.outputs:
        #     script.config.set( 'Musikla', 'outputs', options.outputs )

        if options.outputs:
            for output in options.outputs:
                script.player.add_sequencer( output )
        elif script.config.has_option( 'Musikla', 'output' ):
            script.player.add_sequencer( script.config.get( 'Musikla', 'output' ) )
        else:
            script.player.add_sequencer( self.default_output )

        for lib in options.imports or []:
            script.import_library( lib )

        if script.config.has_option( 'Musikla', 'midi_input' ):
            lib = cast( MidiLibrary, script.context.library( MidiLibrary ) )
            
            lib.set_midi_default_input( script.config.get( 'Musikla', 'midi_input' ) )

        try:
            if options.file == None:
                # Super duper naive repl that accepts only a sequence of one-liners
                for line in sys.stdin:
                    script.execute( line, sync = False, realtime = script.player.realtime )
            else:
                script.execute_file( options.file, sync = False, realtime = script.player.realtime )

            keyboard : KeyboardLibrary = cast( KeyboardLibrary, script.context.library( KeyboardLibrary ) )

            # Wait for the end of the player if there is anything left to play
            await script.join()

            if keyboard != None and keyboard.has_keys:
                await self.keyboard( script.context, keyboard )
        finally:
            script.player.close()
