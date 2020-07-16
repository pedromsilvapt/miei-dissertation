from musikla.parser.printer import CodePrinter
from musikla.core.context import StackFrame
from ..node import Node
from .statement_node import StatementNode
from typing import Tuple, Optional
from musikla.core import Value, Context

class ReturnStatementNode( StatementNode ):
    def __init__ ( self, expression : Node = None, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.expression : Optional[Node] = expression

    def __eval__ ( self, context : Context ):
        stack_frame : Optional[StackFrame] = context.symbols.lookup( 'stack_frame', container = 'stack' )

        if stack_frame is None:
            raise Exception( "Cannot return here, no stack frame found." )

        if self.expression is None:
            stack_frame.ret()
        else:
            val = Value.eval( context, self.expression )

            stack_frame.ret( Value.assignment( val ) )

            return val

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( "return " )

        if self.expression is not None:
            self.expression.to_source( printer )
