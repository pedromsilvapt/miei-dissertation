from .music_node import MusicNode

class MusicSequenceNode( MusicNode ):
    def __init__ ( self, nodes ):
        super().__init__()

        self.expressions = nodes

    def get_events ( self, context ):
        for node in self.expressions:
            for event in node.get_events( context ): 
                yield event
    