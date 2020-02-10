from .expression_node import ExpressionNode
from musikla.core import Value

class NumberLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : (int, int) = None ):
        super().__init__( position )

        self.value = value

    def eval ( self, context, assignment : bool = False ):
        return self.value
