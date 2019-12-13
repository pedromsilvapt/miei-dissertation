from .expression_node import ExpressionNode
from ..node import Node
from core import Value, Music, Context

class BlockNode( ExpressionNode ):
    def __init__ ( self, body : Node, position : (int, int) = None ):
        super().__init__( position )

        self.body = body

    def eval ( self, context : Context ):
        forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

        try:
            return self.body.eval( forked )
        finally:
            context.join( forked )
