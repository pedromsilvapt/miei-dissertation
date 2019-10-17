from .expression_node import ExpressionNode

class FunctionExpressionNode( ExpressionNode ):
    def __init__ ( self, name, parameters ):
        super().__init__()

        self.name = name
        self.parameters = parameters

    def as_assignment ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return None

        return value.as_assignment( context )

    def get_events ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return None

        for event in value.get_events( context ):
            yield event
