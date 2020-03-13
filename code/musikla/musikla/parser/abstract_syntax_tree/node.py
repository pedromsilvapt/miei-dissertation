from typing import Any, Optional, Tuple
from musikla.core import Context

class Node():
    def __init__ ( self, position : Tuple[int, int] = None ):
        self.position : Optional[Tuple[int, int]] = position

    def eval ( self, context : Context ) -> Any:
        return None

    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)

class ValueNode(Node):
    def __init__ ( self, value : Any ):
        self.value : Any = value
    
    def eval ( self, context : Context ):
        return self.value