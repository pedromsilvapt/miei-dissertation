from .expression_node import ExpressionNode
from core import Value, VALUE_KIND_BOOL

class BoolLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : (int, int) = None ):
        super().__init__( position )

        self.value = Value( VALUE_KIND_BOOL, value )

    def eval ( self, context, assignment : bool = False ):
        return self.value
