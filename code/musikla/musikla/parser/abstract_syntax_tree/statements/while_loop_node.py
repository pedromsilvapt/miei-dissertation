from musikla.core import Context, SymbolsScope, Value
from ..node import Node
from .statement_node import StatementNode

class WhileLoopStatementNode( StatementNode ):
    def __init__ ( self, condition : Node, body : Node, position : (int, int) = None ):
        super().__init__( position )

        self.condition : Node = condition
        self.body : Node = body

    def eval ( self, context : Context ):
        condition_value = self.condition.eval( context )

        result = None

        while condition_value:
            result = self.body.eval( context )

            condition_value = self.condition.eval( context )

        return result

