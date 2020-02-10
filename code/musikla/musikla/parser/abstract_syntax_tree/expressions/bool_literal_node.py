from .expression_node import ExpressionNode
from musikla.core import Value

class BoolLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : (int, int) = None ):
        super().__init__( position )

        self.value = value

    def eval ( self, context ):
        return self.value
