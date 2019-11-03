from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context

class SignatureModifierNode( ContextModifierNode ):
    def __init__ ( self, upper = None, lower = None, position : (int, int) = None ):
        super().__init__( position )

        self.upper = upper
        self.lower = lower

    def modify ( self, context : Context ):
        if self.upper != None or self.lower != None:
            context.time_signature = ( self.upper, self.lower )
        elif self.upper != None:
            context.time_signature = ( self.upper, context.time_signature[ 1 ] )
        elif self.lower != None:
            context.time_signature = ( context.time_signature[ 0 ], self.lower )

        yield ContextChangeEvent( context.cursor, "timeSignature", context.time_signature )
