from .. import MusicNode

class BlockContextModifierNode( MusicNode ):
    def __init__ ( self, body ):
        super().__init__()

        self.body = body
    
    def modify ( self, context ):
        pass

    def restore ( self, context ):
        pass

    def get_events ( self, context ):
        block_context = context.fork()

        self.modify( block_context )

        try:
            if self.body != None:
                for event in self.body.eval( block_context ):
                    yield event
        finally:
            self.restore( block_context )

            context.join( block_context )
