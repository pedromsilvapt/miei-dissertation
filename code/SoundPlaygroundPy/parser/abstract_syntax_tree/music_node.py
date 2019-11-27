from .expressions import ExpressionNode
from core import Value, Music

class MusicNode( ExpressionNode ):
    def __init__ ( self, position : (int, int) = None ):
        super().__init__( position )
    
    def get_events ( self, context ):
        return iter( () )

    def eval ( self, context ):
        # FIXME
        if False:
            return SharedMusicEvents( context.fork(), self )

        return Music( self.get_events( context ) )
