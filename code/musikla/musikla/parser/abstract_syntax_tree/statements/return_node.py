from musikla.core.context import StackFrame
from ..node import Node
from .statement_node import StatementNode
from typing import Tuple, Optional
from musikla.core import Value, Context

class ReturnStatementNode( StatementNode ):
    def __init__ ( self, expression : Node = None, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.expression : Optional[Node] = expression

    def eval ( self, context : Context ):
        stack_frame : Optional[StackFrame] = context.symbols.lookup( 'stack_frame', container = 'stack' )

        if stack_frame is None:
            raise Exception( "Cannot return here, no stack frame found." )

        if self.expression is None:
            stack_frame.ret()
        else:
            stack_frame.ret( Value.eval( context, self.expression ) )

        return None
