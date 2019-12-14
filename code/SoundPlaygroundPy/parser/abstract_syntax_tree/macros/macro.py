from ..node import Node
from core import Context

class MacroNode(Node):
    def eval ( self, context : Context ):
        return self.virtual_node.eval( context )
