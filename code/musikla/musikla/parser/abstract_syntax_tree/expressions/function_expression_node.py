from .expression_node import ExpressionNode
from musikla.core import Value
from typing import Callable

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, name, parameters = [], named_parameters = dict(), position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.parameters = parameters
        self.named_parameters = named_parameters

    def eval ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if value == None: 
            raise BaseException( "Calling undefined function %s" % self.name )

        Value.expect( value, Callable )

        return value( context, self.parameters, self.named_parameters )
