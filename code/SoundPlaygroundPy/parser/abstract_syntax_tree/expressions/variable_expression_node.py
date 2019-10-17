from .expression_node import ExpressionNode

class VariableExpressionNode( ExpressionNode ):
    def __init__ ( self, name ):
        super().__init__()

        self.name = name

    def eval ( self, context, assignment : bool = False ):
        value = context.symbols.lookup( self.name )
        
        if value == None: return None

        return value
