from .music_node import MusicNode

class MusicRepeatNode( MusicNode ):
    def __init__ ( self, expression, count ):
        super().__init__()

        self.expression = expression
        self.count = count
    
    def get_events ( self, context ):
        for i in range( self.count ):
            ctx = context.fork()

            try:
                for event in self.expression.eval( ctx ):
                    yield event
            finally:
                context.join( ctx )
