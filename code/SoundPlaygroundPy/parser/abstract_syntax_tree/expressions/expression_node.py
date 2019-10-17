from ..node import Node
from core import Context

class ExpressionNode( Node ):
    def as_assignment ( self, context : Context ):
        raise BaseException("Expression cannot be assigned")
