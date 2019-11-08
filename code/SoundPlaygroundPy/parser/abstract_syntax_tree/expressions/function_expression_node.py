from .expression_node import ExpressionNode
from core import VALUE_KIND_CALLABLE

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, name, parameters = [], named_parameters = dict(), position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.parameters = parameters
        self.named_parameters = named_parameters

    def eval ( self, context, assignment : bool = False ):
        value = context.symbols.lookup( self.name )
        
        if value == None: 
            raise BaseException( "Calling undefined function %s" % self.name )

        if value.kind != VALUE_KIND_CALLABLE:
            raise BaseException( f"Value is of type {value.kind}, expected callable." )

        return value.call( context, self.parameters, self.named_parameters, assignment = assignment )
