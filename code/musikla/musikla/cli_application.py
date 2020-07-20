from asyncio.tasks import sleep
import sys
import argparse
import os

from musikla.core import Context
from musikla.libraries import KeyboardLibrary, MidiLibrary
from musikla.audio import Player
from musikla.audio.sequencers import Sequencer, SequencerFactory
from musikla.parser.abstract_syntax_tree.expressions import Object
from musikla import Script
from typing import List, Optional, cast
from colorama import init
from shlex import shlex, split

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

    def split_argv ( self, argv : List[str], separators : List[str] ) -> List[List[str]]:
        groups : List[List[str]] = []

        start = 0

        for i in range( len( argv ) ):
            if argv[ i ] in separators:
                groups.append( argv[ start : i ] )

                start = i
        
        groups.append( argv[ start: ] )

        return groups

    def parse_outputs_args ( self, player : Player, argvs : List[List[str]] ) -> List[Sequencer]:
        sequencers : List[Sequencer] = []

        for argv in argvs:
            format : Optional[str] = None

            output : str = argv[ 1 ]
            
            if len( argv ) >= 4 and ( argv[ 2 ] == '-f' or argv[ 2 ] == '--format' ):
                format = argv[ 3 ]

                argv = argv[ 4: ]
            else:
                argv = argv[ 2: ]

            if format is not None:
                sequencers.append( player.make_sequencer_from_format( format, output, argv ) )
            else:
                sequencers.append( player.make_sequencer_from_uri( output, argv ) )

        return sequencers

    async def run ( self ):
        init()

        parser = argparse.ArgumentParser( description = 'Evaluate musical expression' )

        parser.add_argument( 'file', type = str, nargs = '?', help = 'Files to evaluate. No file means the input will be read from the stdin' )
        parser.add_argument( '-c', '--code', type = str, help = 'Execute a piece of code' )
        parser.add_argument( '-i', '--import', dest = 'imports', action = 'append', type = str, help = 'Import an additional library. These can be builtin libraries, or path to .ml and .py files' )
        parser.add_argument( '-o', '--output', dest = 'outputs', type = str, action = 'append', help = 'Where to output to. By default outputs the sounds to the device\'s speakers.' )
        parser.add_argument( '-f', '--format', dest = 'formats', type = str, action = 'append', help = 'Type of output to use' )
        parser.add_argument( '-v', '--variable', dest = 'variables', nargs=2, metavar=('name', 'value'), type = str, action = 'append', help = 'Set a custom variable available under $sys\\vars' )
        parser.add_argument( '--midi', type = str, help = 'Use a custom MIDI port by default when no name is specified' )
        parser.add_argument( '--soundfont', type = str, help = 'Use a custom soundfont .sf2 file' )
        parser.add_argument( '--print-events', dest = 'print_events', action='store_true', help = 'Print events (notes) to the console as they are played.' )
        parser.add_argument( '--profile', dest = 'profile', action='store_true', help = 'Measure and display total parse times' )
        parser.add_argument( '--traceback', dest = 'traceback', action='store_true', help = 'Display error tracebacks (aka stacktraces)' )
        parser.add_argument( '--skip-parser-cache', dest = 'skip_parser_cache', action='store_true', help = 'Force the parser to rebuild the grammar cache on disk' )

        if '--' in self.argv:
            index = self.argv.index( '--' )

            argv = self.argv[:index]
            internal_args = self.argv[index + 1:]
        else:
            argv = self.argv
            internal_args = []

        argv = self.split_argv( argv, [ '-o', '--output' ] )

        options = parser.parse_args( argv[ 0 ] )

        script = Script( symbols = {
            'sys\\args': internal_args,
            'sys\\vars': Object( options.variables or [] )
        } )

        if options.profile:
            print( "PARSE (AUTOLOAD): ", script.parser.time_spent * 1000, "ms" )

        if options.skip_parser_cache:
            script.parser.read_cache = False

        if options.traceback:
            script.print_tracebacks = True

        if argv[ 1: ]:
            sequencers = self.parse_outputs_args( script.player, argv[ 1: ] )
        elif script.config.has_option( 'Musikla', 'output' ):
            output_array = split( script.config.get( 'Musikla', 'output' ) )
            
            split_output_array = self.split_argv( output_array, [ '-o', '--output' ] )

            sequencers = self.parse_outputs_args( script.player, split_output_array[ 1: ] )
        else:
            sequencers = []

        script.player.print_events = bool( options.print_events )
        
        if not script.config.has_section( 'Musikla' ):
            script.config.add_section( 'Musikla' )

        if options.soundfont != None:
            script.config.set( 'Musikla', 'soundfont', options.soundfont )

        if options.midi != None:
            script.config.set( 'Musikla', 'midi_input', options.midi )

        if sequencers:
            for sequencer in sequencers:
                script.player.add_sequencer( sequencer )
        else:
            script.player.add_sequencer( self.default_output )

        for lib in options.imports or []:
            script.import_library( lib )

        if script.config.has_option( 'Musikla', 'midi_input' ):
            lib = cast( MidiLibrary, script.context.library( MidiLibrary ) )
            
            lib.set_midi_default_input( script.config.get( 'Musikla', 'midi_input' ) )

        try:
            if options.code is not None:
                script.execute( options.code, sync = False, realtime = script.player.realtime )
            elif options.file is None:
                # Super duper naive repl that accepts only a sequence of one-liners
                print( "Welcome to the Musikla REPL. Type \"quit();\" to exit." )
                print( '>>> ', end = '' )
                for line in sys.stdin:
                    try:
                        if line == 'quit();':
                            break

                        script.execute( line, sync = False, realtime = script.player.realtime )
                    except:
                        print( sys.exc_info()[ 0 ] )

                    print( '>>> ', end = '' )
            else:
                script.execute_file( options.file, sync = False, realtime = script.player.realtime )

            if options.profile:
                print( "PARSE (TOTAL): ", script.parser.time_spent * 1000, "ms" )

            keyboard : KeyboardLibrary = cast( KeyboardLibrary, script.context.library( KeyboardLibrary ) )

            # Wait for the end of the player if there is anything left to play
            await script.join()

            if keyboard != None and keyboard.has_keys:
                await self.keyboard( script.context, keyboard )
            else:
                await sleep(2)
        finally:
            script.player.close()
