from musikla.parser.printer import CodePrinter
from typing import Tuple
from .expression_node import ExpressionNode
from musikla.core import Music

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.name = name

    def eval ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if isinstance( value, Music ):
            return Music( value.expand( context ) )

        return value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( '$' + self.name )