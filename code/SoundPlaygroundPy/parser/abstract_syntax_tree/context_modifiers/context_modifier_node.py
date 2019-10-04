from .. import MusicNode

class ContextModifierNode( MusicNode ):
    def modify ( self, context ):
        pass

    def get_events ( self, context ):
        self.modify( context )

        return iter( () )
