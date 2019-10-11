from .expression_node import ExpressionNode

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name ):
        super().__init__()

        self.name = name

    def as_assignment ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return None

        return value.as_assignment( context )

    def get_events ( self, context ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return None

        for event in value.get_events( context ):
            yield event
