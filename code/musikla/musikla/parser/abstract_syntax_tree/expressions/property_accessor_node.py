from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Context
from ..node import Node

class PropertyAccessorNode( Node ):
    def __init__ ( self, expression : Node, name : Node, as_attr : bool, position : Tuple[int, int, int] = None ):
        super().__init__( position )
        
        self.expression : Node = expression
        self.name : Node = name
        self.as_attr : bool = as_attr

    def assign ( self, context, value, local : bool = False ):
        expr = self.expression.eval( context )
        name = self.name.eval( context )

        if self.as_attr:
            setattr( expr, name, value )
        else:
            expr[ name ] = value
        
    def lookup_assign ( self, context, value_fn, local : bool = False ):
        expr = self.expression.eval( context )
        name = self.name.eval( context )

        if self.as_attr:
            value = getattr( expr, name, None )
        else:
            value = expr[ name ]

        value = value_fn( value )

        if self.as_attr:
            setattr( expr, name, value )
        else:
            expr[ name ] = value

    def __eval__ ( self, context : Context ):
        expr = self.expression.eval( context )
        name = self.name.eval( context )

        if self.as_attr:
            return getattr( expr, name, None )
        else:
            return expr[ name ]

    def to_source ( self, printer : CodePrinter ):
        from .string_literal_node import StringLiteralNode

        self.expression.to_source( printer )

        if isinstance( self.name, StringLiteralNode ):
            printer.add_token( '::' + self.name.value )
        else:
            with printer.block( '::[', ']' ):
                self.name.to_source( printer )