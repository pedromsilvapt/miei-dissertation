from core import Value, Music
from .music_node import MusicNode

class MusicSequenceNode( MusicNode ):
    def __init__ ( self, nodes, position : (int, int) = None ):
        super().__init__( position )

        self.expressions = nodes

    def get_events ( self, context ):
        for node in self.expressions:
            value = node.eval( context )

            if isinstance( value, Music ):
                for event in value:
                    yield event
    
    def __iter__ ( self ):
        return iter( self.expressions )
