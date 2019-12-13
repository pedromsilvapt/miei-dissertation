from .statement_node import StatementNode
from core import Value, Context

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, expression, local : bool = False, position : (int, int) = None ):
        super().__init__( position )

        self.name : str = name
        self.expression = expression
        self.local : bool = local

    def eval ( self, context : Context ):
        context.symbols.assign( self.name, Value.assignment( self.expression.eval( context.fork() ) ), local = self.local )

        return None
