from .expression_node import ExpressionNode
from musikla.core import Value, Music

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name, position : (int, int) = None ):
        super().__init__( position )

        self.name = name

    def eval ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if isinstance( value, Music ):
            return Music( value.expand( context ) )

        return value
