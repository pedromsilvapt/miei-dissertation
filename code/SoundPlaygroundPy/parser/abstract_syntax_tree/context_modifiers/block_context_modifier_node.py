from .. import MusicNode

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

        if events != None:
            for event in events: yield event

        try:
            if self.body != None:
                for event in self.body.eval( block_context ):
                    yield event
        finally:
            self.restore( block_context )

            context.join( block_context )
