from musikla.core import Context, Music
from .keyboard import Keyboard
from fractions import Fraction

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
