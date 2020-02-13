from musikla.core import Music
from .music_node import MusicNode
from musikla.core import merge_sorted

class MusicParallelNode( MusicNode ):
    def __init__ ( self, nodes, position : (int, int) = None ):
        super().__init__( position )
        
        self.expressions = nodes
    
    def fork_and_get_events ( self, node, forks, context ):
        forked = context.fork()

        forks.append( forked )

        value = node.eval( forked )

        if isinstance( value, Music ):
            return value.expand( forked )

        return []

    def get_events ( self, context ):
        forks = []

        notes = map( lambda node: self.fork_and_get_events( node, forks, context ), self.expressions )
        notes = merge_sorted( notes, lambda note: note.timestamp )

        try:
            for note in notes:
                yield note
        finally:
            context.join( *forks )
        