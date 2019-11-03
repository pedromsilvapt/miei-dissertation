from .statement_node import StatementNode

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, expression, position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.expression = expression

    def eval ( self, context, assignment : bool = False ):
        context.symbols.assign( self.name, self.expression.eval( context, assignment = True ) )

        return None
