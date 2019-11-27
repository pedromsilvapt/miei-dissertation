from .statement_node import StatementNode
from core import Value

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, expression, position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.expression = expression

    def eval ( self, context ):
        context.symbols.assign( self.name, Value.assignment( self.expression.eval( context.fork() ) ) )

        return None
