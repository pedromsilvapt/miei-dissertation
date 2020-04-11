from typing import Tuple
from musikla.parser.printer import CodePrinter
from .expression_node import ExpressionNode

class BoolLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.value = value

    def eval ( self, context ):
        return self.value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'true' if self.value else 'false' )
