from .. import MusicNode
from core import Music

class BlockContextModifierNode( MusicNode ):
    def __init__ ( self, body, position : (int, int) = None ):
        super().__init__( position )

        self.body = body
    
    def modify ( self, context ):
        pass

    def restore ( self, context ):
        pass

    def get_events ( self, context ):
        block_context = context.fork()

        events = self.modify( block_context )

        if isinstance( events, Music ):
            for event in events: yield event

        try:
            if self.body != None:
                events = self.body.eval( block_context )

                if isinstance( events, Music ):
                    for event in events: yield event

            events = self.restore( block_context )

            if isinstance( events, Music ):
                for event in events: yield event
        finally:
            context.join( block_context )
