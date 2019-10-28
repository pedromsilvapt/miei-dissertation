from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context

class OctaveModifierNode( ContextModifierNode ):
    def __init__ ( self, octave ):
        super().__init__()

        self.octave = octave
        
    def modify ( self, context : Context ):
        context.octave = self.octave

        yield ContextChangeEvent( context.cursor, "octave", context.octave )
