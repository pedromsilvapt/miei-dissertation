from musikla.parser.printer import CodePrinter
from musikla.parser.abstract_syntax_tree.expressions.variable_expression_node import VariableExpressionNode
from musikla.parser.abstract_syntax_tree.expressions.property_accessor_node import PropertyAccessorNode
from .expression_node import ExpressionNode
from musikla.core import Value
from musikla.core.callable_python_value import CallablePythonValue
from typing import Callable, Tuple, cast

class FunctionChainExpressionNode( ExpressionNode ):
    def __init__ ( self, left_hand, right_hand, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.left_hand = left_hand
        self.right_hand = right_hand

        self.right_hand.expression = left_hand
        
        if position is not None:
            self.right_hand.position = position
    
    @property
    def position ( self ):
        return self.right_hand.position

    @position.setter
    def position( self, value ):
        if hasattr( self, 'right_hand' ) and self.right_hand is not None:
            self.right_hand.position = value

    @property
    def expression ( self ):
        return self.left_hand.expression

    @expression.setter
    def expression( self, value ):
        self.left_hand.expression = value

    def __eval__ ( self, context ):
        return self.right_hand.eval( context )

    def to_source ( self, printer : CodePrinter ):
        self.right_hand.to_source( printer )

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, expression, parameters = [], named_parameters = dict(), position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.expression : ExpressionNode = expression
        self.parameters = parameters
        self.named_parameters = named_parameters

    def __eval__ ( self, context ):
        value = self.expression.eval( context )
        
        if value == None: 
            if isinstance( self.expression, VariableExpressionNode ):
                raise BaseException( f"Calling undefined function { cast( VariableExpressionNode, self.expression ).name }" )
            elif isinstance( self.expression, PropertyAccessorNode ):
                method_name = cast( PropertyAccessorNode, self.expression ).name.eval( context )
                object_name = CodePrinter().print( cast( PropertyAccessorNode, self.expression ).expression )

                raise BaseException( f"Calling undefined function '{ method_name }' in '{ object_name }'" )
            else:
                raise BaseException( "Calling undefined function" )

        return CallablePythonValue.call( value, context, self.parameters, self.named_parameters )

    def to_source ( self, printer : CodePrinter ):
        from .variable_expression_node import VariableExpressionNode

        if isinstance( self.expression, VariableExpressionNode ):
            printer.add_token( self.expression.name )
        else:
            self.expression.to_source( printer )
        
        with printer.block( '(', ')' ):
            for i in range( len( self.parameters ) ):
                if i > 0:
                    printer.add_token( '; ' )
                
                self.parameters[ i ].to_source( printer )

            not_first = bool( self.parameters )

            for key, node in self.named_parameters.items():
                if not_first:
                    printer.add_token( '; ' )

                printer.add_token( key + ' = ' )
                
                node.to_source( printer )

                not_first = True
