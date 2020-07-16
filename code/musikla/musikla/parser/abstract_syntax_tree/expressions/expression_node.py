from typing import Any
from ..node import Node
from musikla.core import Context

class ExpressionNode( Node ):
    def __eval__ ( self, context : Context ) -> Any:
        raise BaseException("Abstract Expression cannot be evaluated")
