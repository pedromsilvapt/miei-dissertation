from .. import MusicNode

class ContextModifierNode( MusicNode ):
    def modify ( self, context ):
        pass

    def get_events ( self, context ):
        value = self.modify( context )

        if value != None:
            return value

        return iter( () )
