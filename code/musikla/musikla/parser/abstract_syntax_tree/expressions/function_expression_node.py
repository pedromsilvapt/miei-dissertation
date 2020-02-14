from .expression_node import ExpressionNode
from musikla.core import Value
from typing import Callable

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, expression, parameters = [], named_parameters = dict(), position : (int, int) = None ):
        super().__init__( position )

        self.expression : ExpressionNode = expression
        self.parameters = parameters
        self.named_parameters = named_parameters

    def eval ( self, context ):
        value = self.expression.eval( context )
        
        if value == None: 
            raise BaseException( "Calling undefined function" )

        Value.expect( value, Callable )

        return value( context, self.parameters, self.named_parameters )
