from .expression_node import ExpressionNode
from core import Value, VALUE_KIND_STRING

class StringLiteralNode( ExpressionNode ):
    def __init__ ( self, value ):
        super().__init__()

        self.value = Value( VALUE_KIND_STRING, value )

    def eval ( self, context, assignment : bool = False ):
        return self.value