from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context

class TempoModifierNode( ContextModifierNode ):
    def __init__ ( self, tempo, position : (int, int) = None ):
        super().__init__( position )

        self.tempo = tempo

    def modify ( self, context : Context ):
        context.tempo = self.tempo

        yield ContextChangeEvent( context.cursor, "tempo", context.tempo )
