from musikla.parser.printer import CodePrinter
from typing import Optional, Tuple
from ..node import Node
from musikla.core import Context

class MacroNode(Node):
    def __init__ ( self, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.virtual_node : Optional[Node] = None

    def eval ( self, context : Context ):
        return self.virtual_node.eval( context )

    def to_source ( self, printer : CodePrinter ):
        self.virtual_node.to_source( printer )