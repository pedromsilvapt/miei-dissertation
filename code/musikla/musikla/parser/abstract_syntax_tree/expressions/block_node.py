from typing import Tuple
from .expression_node import ExpressionNode
from ..node import Node
from musikla.core import Context

class BlockNode( ExpressionNode ):
    def __init__ ( self, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.body = body

    def eval ( self, context : Context ):
        forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

        try:
            return self.body.eval( forked )
        finally:
            context.join( forked )
