from .expression_node import ExpressionNode
from core import Value

class NoneLiteralNode( ExpressionNode ):
    def __init__ ( self, position : (int, int) = None ):
        super().__init__( position )

        self.value = None

    def eval ( self, context, assignment : bool = False ):
        return self.value
