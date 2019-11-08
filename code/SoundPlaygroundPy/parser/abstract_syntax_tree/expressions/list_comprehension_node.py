from core import Context, Value, VALUE_KIND_OBJECT
from ..node import Node
from ..expressions import ExpressionNode

# Since returns values of kind OBJECT, this node is not ready for primetime yet.
# Used as a placeholder for the keyboard creation macro
class ListComprehensionNode(ExpressionNode):
    def __init__ ( self, expression : Node, variable : str, min : Node, max : Node, condition : Node = None, position : (int, int) = None ):
        super().__init__( position )

        self.expression : Node= expression
        self.variable : str = variable
        self.min : Node = min
        self.max : Node = max
        self.condition : Node = condition
    
    def eval ( self, context, assignment : bool = False ): 
        return Value.create( None )
