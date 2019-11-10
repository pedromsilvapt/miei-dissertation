from core import Context, SymbolsScope, Value
from ..node import Node
from .statement_node import StatementNode

class IfStatementNode( StatementNode ):
    def __init__ ( self, condition : Node, body : Node, position : (int, int) = None ):
        super().__init__( position )

        self.condition : Node = max
        self.body : Node = body

    def eval ( self, context : Context, assignment : bool = False ):
        condition_value : Value = self.condition.eval( context )

        if condition_value != None and condition_value.is_truthy:
            result = body.eval( forked )

        return result
