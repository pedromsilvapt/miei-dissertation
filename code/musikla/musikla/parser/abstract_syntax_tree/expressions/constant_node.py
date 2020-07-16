from musikla.parser.printer import CodePrinter
from .expression_node import ExpressionNode
from typing import Any, Tuple

class ConstantNode( ExpressionNode ):
    def __init__ ( self, value : Any, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.value : Any = value

    def __eval__ ( self, context ):
        return self.value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( str( self.value ) )
