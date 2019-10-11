from .statement_node import StatementNode

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, expression ):
        super().__init__()

        self.name = name
        self.expression = expression

    def get_events ( self, context ):
        context.symbols.assign( self.name, self.expression.as_assignment( context ) )

        return iter(())
