from .node import Node

class MusicNode( Node ):
    def __init__ ( self ):
        super().__init__()
    
    def get_events ( self, context ):
        return iter( () )
