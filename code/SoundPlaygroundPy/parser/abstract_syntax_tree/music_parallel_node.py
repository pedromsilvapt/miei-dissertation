from core import Music
from .music_node import MusicNode
from py_linq import Enumerable

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

        # TODO add merge_sorted extension method to enumerables
        notes = Enumerable( self.expressions )\
            .select( lambda node: self.fork_and_get_events( node, forks, context ) )\
            .merge_sorted( lambda note: note.timestamp )

        try:
            for note in notes:
                yield note
        finally:
            context.join( *forks )
        