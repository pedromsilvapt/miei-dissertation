from musikla.parser.abstract_syntax_tree.expressions.variable_expression_node import VariableExpressionNode
from .expression_node import ExpressionNode
from musikla.core import Value
from musikla.core.callable_python_value import CallablePythonValue
from typing import Callable, Tuple, cast

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, expression, parameters = [], named_parameters = dict(), position : Tuple[int, int] = None ):
        super().__init__( position )

        self.expression : ExpressionNode = expression
        self.parameters = parameters
        self.named_parameters = named_parameters

    def eval ( self, context ):
        value = self.expression.eval( context )
        
        if value == None: 
            if isinstance( self.expression, VariableExpressionNode ):
                raise BaseException( f"Calling undefined function { cast( VariableExpressionNode, self.expression ).name }" )
            else:
                raise BaseException( "Calling undefined function" )

        return CallablePythonValue.call( value, context, self.parameters, self.named_parameters )
