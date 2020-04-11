from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Context
from ..node import Node

class PropertyAccessorNode( Node ):
    def __init__ ( self, expression : Node, name : Node, position : Tuple[int, int] = None ):
        super().__init__( position )
        
        self.expression : Node = expression
        self.name : Node = name

    def eval ( self, context : Context, assignment : bool = False ):
        expr = self.expression.eval( context )
        name = self.name.eval( context )

        if type( name ) is int:
            return expr[ name ]
        else:
            return getattr( expr, name, None )

    def to_source ( self, printer : CodePrinter ):
        from .string_literal_node import StringLiteralNode

        self.expression.to_source( printer )

        if isinstance( self.name, StringLiteralNode ):
            printer.add_token( '::' + self.name.value )
        else:
            with printer.block( '::[', ']' ):
                self.name.to_source( printer )