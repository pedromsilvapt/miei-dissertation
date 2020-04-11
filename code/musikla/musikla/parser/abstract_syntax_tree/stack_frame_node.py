from musikla.parser.printer import CodePrinter
from typing import Tuple
from .node import Node
from musikla.core import Value, StackFrame, Context

class StackFrameNode( Node ):
    def __init__ ( self, child : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.child : Node = child
    
    def to_source ( self, printer : CodePrinter ):
        self.child.to_source( printer )

    def eval ( self, context : Context ):
        context.symbols.assign( 'stack_frame', StackFrame(), container = 'stack' )

        return Value.eval( context, self.child )
