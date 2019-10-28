from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context

class VelocityModifierNode( ContextModifierNode ):
    def __init__ ( self, velocity ):
        super().__init__()

        self.velocity = velocity

    def modify ( self, context : Context ):
        context.velocity = self.velocity;

        yield ContextChangeEvent( context.cursor, "velocity", context.velocity )
