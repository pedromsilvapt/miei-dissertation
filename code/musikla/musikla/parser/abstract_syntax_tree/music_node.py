from .expressions import ExpressionNode
from musikla.core import Value, Music

class MusicNode( ExpressionNode ):
    def __init__ ( self, position : (int, int) = None ):
        super().__init__( position )
    
    def get_events ( self, context ):
        return iter( () )

    def eval ( self, context ):
        return Music( self.get_events( context ) )