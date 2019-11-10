from core import Context, SymbolsScope, Value
from ..node import Node
from .statement_node import StatementNode

class IfStatementNode( StatementNode ):
    def __init__ ( self, condition : Node, body : Node, else_body : Node = None, position : (int, int) = None ):
        super().__init__( position )

        self.condition : Node = condition
        self.body : Node = body
        self.else_body : Node = else_body

    def eval ( self, context : Context, assignment : bool = False ):
        condition_value : Value = self.condition.eval( context )

        if condition_value != None and condition_value.is_truthy:
            result = self.body.eval( context )
        elif self.else_body != None:
            result = self.else_body.eval( context )
        else:
            result = Value.create( None )

        return result

