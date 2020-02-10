from ..node import Node
from musikla.core import Context

class ExpressionNode( Node ):
    def eval ( self, context : Context ):
        raise BaseException("Abstract Expression cannot be evaluated")
