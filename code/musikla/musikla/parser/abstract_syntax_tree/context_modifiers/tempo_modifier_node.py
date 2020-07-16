from musikla.parser.printer import CodePrinter
from typing import Tuple
from .context_modifier_node import ContextModifierNode
from musikla.core.events import ContextChangeEvent
from musikla.core import Context, Voice

class TempoModifierNode( ContextModifierNode ):
    def __init__ ( self, tempo, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.tempo = tempo

    def apply ( self, voice : Voice ):
        voice.tempo = self.tempo

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( tempo = self.tempo )

        yield ContextChangeEvent( context.cursor, "tempo", context.voice.tempo, context.voice, 0 )
        
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'T' + str( self.tempo ) )
