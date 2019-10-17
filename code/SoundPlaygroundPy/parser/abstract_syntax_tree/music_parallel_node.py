from .music_node import MusicNode
from py_linq import Enumerable

class MusicParallelNode( MusicNode ):
    def __init__ ( self, nodes ):
        self.expressions = nodes
    
    def fork_and_get_events ( self, node, forks, context ):
        forked = context.fork()

        forks.append( forked )

        return node.eval( forked )

    def get_events ( self, context ):
        forks = []

        # TODO add merge_sorted extension method to enumerables
        notes = Enumerable( self.expressions )\
            .select( lambda node: self.fork_and_get_events( node, forks, context ) )\
            .merge_sorted( lambda note: note.timestamp )

        try:
            for note in notes:
                yield note
        finally:
            context.join( *forks )
        