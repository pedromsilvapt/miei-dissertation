from ..node import Node
from .expression_node import ExpressionNode
from core import Value, Context

class UnaryOperatorNode( ExpressionNode ):
    def __init__ ( self, node : Node, position : (int, int) = None ):
        super().__init__( position )

        self.node : Node = node

    def eval ( self, context, assignment : bool = False ):
        return None

class NotOperatorNode ( UnaryOperatorNode ):
    def eval ( self, context : Context, assignment : bool = False ):
        value = self.node.eval( context )

        return not bool( value )
