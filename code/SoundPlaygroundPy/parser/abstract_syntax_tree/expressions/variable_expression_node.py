from .expression_node import ExpressionNode
from core import Value, VALUE_KIND_MUSIC, VALUE_KIND_NONE

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name, position : (int, int) = None ):
        super().__init__( position )

        self.name = name

    def eval ( self, context, assignment : bool = False ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return Value( VALUE_KIND_NONE, None )

        if value.kind == VALUE_KIND_MUSIC and not assignment:
            return Value( VALUE_KIND_MUSIC, value.value.get_events( context ) )

        return value
