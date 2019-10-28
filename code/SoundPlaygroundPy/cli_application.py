import sys
import argparse
from audio import MidiPlayer
from core import Context, Value
from parser import Parser
from libraries import KeyboardLibrary, StandardLibrary, MusicLibrary

class CliApplication:
    def __init__ ( self, argv,  ):
        self.argv = argv
        self.builtin_libraries = {
            'std': StandardLibrary,
            'keyboard': KeyboardLibrary,
            'music': MusicLibrary
        }
        self.parser = Parser()
        self.player = None

    def create_context ( self ):
        return Context.create()

    def import_library ( self, context : Context, library : str ):
        if library.lower() in self.builtin_libraries:
            instance = self.builtin_libraries[ library.lower() ]()

            context.link( instance )
        else:
            ast = self.parser.parse_file( library )

            ast.eval( context )

    def eval ( self, context, ast ):
        value = ast.eval( context )

        if value and value.is_music:
            self.player.play_more( value )


    def run ( self ):
        parser = argparse.ArgumentParser( description = 'Evaluate musical expression' )

        parser.add_argument( 'file', type = str, nargs = '?', help = 'Files to evaluate. No file means the input will be read from the stdin' )
        parser.add_argument( '-i', '--import', dest = 'imports', action = 'append', type = str, help = 'Import an additional library. These can be builtin libraries, or path to .ml and .py files' )
        parser.add_argument( '-o', '--output', type = str, help = 'Where to output to. By default outputs the sounds to the device\'s speakers.' )
        parser.add_argument( '--soundfont', type = str, help = 'Use a custom soundfont .sf2 file' )
        
        options = parser.parse_args( self.argv )

        self.player = MidiPlayer( options.output or "pulseaudio" )

        if options.soundfont != None:
            self.player.soundfont = options.soundfont

        context = self.create_context()

        # Always import the std library
        self.import_library( context, 'std' )
        self.import_library( context, 'music' )

        for lib in options.imports:
            self.import_library( context, lib )

        if options.file == None:
            # Super duper naive repl that accepts only a sequence of one-liners
            for line in sys.stdin:
                ast = self.parser.parse( line )

                self.eval( context, ast )    
        else:
            ast = self.parser.parse_file( options.file )

            self.eval( context, ast )

        # Wait for the end of the player if there is anything left to play
        self.player.join()

