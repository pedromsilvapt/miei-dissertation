from .expression_node import ExpressionNode
from typing import Any, Tuple

class ConstantNode( ExpressionNode ):
    def __init__ ( self, value : Any, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.value : Any = value

    def eval ( self, context ):
        return self.value
