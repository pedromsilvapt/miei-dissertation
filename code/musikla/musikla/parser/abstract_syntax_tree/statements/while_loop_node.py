from typing import Tuple
from musikla.parser.printer import CodePrinter
from musikla.core import Context
from ..node import Node
from .statement_node import StatementNode

class WhileLoopStatementNode( StatementNode ):
    def __init__ ( self, condition : Node, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.condition : Node = condition
        self.body : Node = body

    def eval ( self, context : Context ):
        condition_value = self.condition.eval( context )

        result = None

        while condition_value:
            result = self.body.eval( context.fork( symbols = context.symbols.fork( opaque = False ) ) )

            condition_value = self.condition.eval( context )

        return result

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'while ' )

        with printer.block( '(', ')' ):
            self.condition.to_source( printer )

        with printer.block():
            self.body.to_source( printer )
