from .. import MusicNode

class ContextModifierNode( MusicNode ):
    def apply ( self, voice ):
        pass

    def modify ( self, context ):
        pass

    def get_events ( self, context ):
        return self.modify( context )
