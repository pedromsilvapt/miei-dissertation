from core import Value
from .music_node import MusicNode

class MusicSequenceNode( MusicNode ):
    def __init__ ( self, nodes, position : (int, int) = None ):
        super().__init__( position )

        self.expressions = nodes

    def get_events ( self, context ):
        for node in self.expressions:
            value : Value = node.eval( context )

            if value != None and value.is_music:
                for event in value:
                    yield event
    