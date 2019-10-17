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

    def eval ( self, context, assignment : bool = False ):
        value = context.symbols.lookup( self.name )
        
        if value == None: 
            raise BaseException( "Calling undefined function" )

        if value.kind != VALUE_KIND_CALLABLE:
            raise BaseException( f"Value is of type {value.kind}, expected callable." )

        return value.value( context, self.parameters )
