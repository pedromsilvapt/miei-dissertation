from typing import Tuple
from .expression_node import ExpressionNode
from ..node import Node
from ..stack_frame_node import StackFrameNode
from musikla.core import Context

class BlockNode( ExpressionNode ):
    def __init__ ( self, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.body = StackFrameNode( body, position = position )

    def eval ( self, context : Context ):
        forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

        try:
            return self.body.eval( forked )
        finally:
            context.join( forked )
