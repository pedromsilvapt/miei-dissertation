from musikla.parser.printer import CodePrinter
from typing import Tuple
from .context_modifier_node import ContextModifierNode
from musikla.core.events import ContextChangeEvent
from musikla.core import Context, Voice

class OctaveModifierNode( ContextModifierNode ):
    def __init__ ( self, octave, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.octave = octave
        
    def apply ( self, voice : Voice ):
        voice.octave = self.octave

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( octave = self.octave )

        yield ContextChangeEvent( context.cursor, "octave", context.voice.octave, context.voice, 0 )
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'O' + str( self.octave ) )