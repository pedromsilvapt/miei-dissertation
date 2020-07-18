from musikla.parser.printer import CodePrinter
from typing import Optional, Tuple
from .node import Node
from musikla.core import Value, StackFrame, Context

class StackFrameNode( Node ):
    def __init__ ( self, child : Optional[Node], position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.child : Optional[Node] = child
    
    def to_source ( self, printer : CodePrinter ):
        if self.child is not None:
            self.child.to_source( printer )

    def __eval__ ( self, context : Context ):
        if self.child is not None:
            context.symbols.assign( 'stack_frame', StackFrame(), container = 'stack' )

            return Value.eval( context, self.child )
