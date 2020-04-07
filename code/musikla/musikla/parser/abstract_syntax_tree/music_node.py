from typing import Tuple
from .expressions import ExpressionNode
from musikla.core import Music

class MusicNode( ExpressionNode ):
    def __init__ ( self, position : Tuple[int, int] = None ):
        super().__init__( position )
    
    def get_events ( self, context ):
        return iter( () )

    def eval ( self, context ):
        return Music( self.get_events( context ) )
