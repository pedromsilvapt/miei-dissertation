from musikla.parser.printer import CodePrinter
from typing import Tuple
from .expression_node import ExpressionNode

class StringLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.value = value

    def __eval__ ( self, context, assignment : bool = False ):
        return self.value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( "'" + self.value + "'" )