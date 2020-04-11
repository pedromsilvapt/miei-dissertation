from typing import Optional, Tuple
from musikla.core import Context, Value
from ..node import Node
from ..expressions import ExpressionNode

# Since returns values of kind OBJECT, this node is not ready for primetime yet.
# Used as a placeholder for the keyboard creation macro
class ListComprehensionNode(ExpressionNode):
    def __init__ ( self, expression : Node, variable : str, min : Node, max : Node, condition : Node = None, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.expression : Node= expression
        self.variable : str = variable
        self.min : Node = min
        self.max : Node = max
        self.condition : Optional[Node] = condition
    
    def eval ( self, context, assignment : bool = False ): 
        return None
