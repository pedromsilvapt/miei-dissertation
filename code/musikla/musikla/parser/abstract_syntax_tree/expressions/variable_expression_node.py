from musikla.parser.printer import CodePrinter
from typing import Tuple
from .expression_node import ExpressionNode
from musikla.core import Music

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.name = name

    def assign ( self, context, value, local : bool = False ):
        context.symbols.assign( self.name, value, local = local )

    def lookup_assign ( self, context, value_fn, local : bool = False ):
        value = context.symbols.lookup( self.name, recursive = not local )

        value = value_fn( value )

        context.symbols.assign( self.name, value, local = local )

    def eval ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if isinstance( value, Music ):
            return Music( value.expand( context ) )

        return value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( '$' + self.name )