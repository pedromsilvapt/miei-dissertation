from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context

class LengthModifierNode( ContextModifierNode ):
    def __init__ ( self, length ):
        super().__init__()

        self.length = length
        
    def modify ( self, context : Context ):
        context.value = self.length

        yield ContextChangeEvent( context.cursor, "length", context.value )
