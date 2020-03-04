from .expression_node import ExpressionNode
from typing import List
from musikla.core import Value

class ArrayLiteralNode( ExpressionNode ):
    def __init__ ( self, values : List[ExpressionNode], position : (int, int) = None ):
        super().__init__( position )

        self.values : List[ExpressionNode] = values

    def eval ( self, context ):
        return [ Value.assignment( Value.eval( context.fork(), node ) ) for node in self.values ]
