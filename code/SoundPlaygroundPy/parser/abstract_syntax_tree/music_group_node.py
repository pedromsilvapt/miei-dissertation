from .music_node import MusicNode

class MusicGroupNode( MusicNode ):
    def __init__ ( self, expression, position : (int, int) = None ):
        super().__init__( position )
        
        self.expression = expression

    def get_events ( self, context ):
        forked = context.fork()

        try:
            for event in self.expression.eval( context ):
                yield event
        finally:
            context.join( forked )
