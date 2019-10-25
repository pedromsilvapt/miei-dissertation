from .expressions import ExpressionNode
from core import Value, VALUE_KIND_MUSIC

class MusicNode( ExpressionNode ):
    def __init__ ( self ):
        super().__init__()
    
    def get_events ( self, context ):
        return iter( () )

    def eval ( self, context, assignment : bool = False ):
        if assignment == True:
            return Value( VALUE_KIND_MUSIC, SharedMusicEvents( context.fork(), self ) )

        return Value( VALUE_KIND_MUSIC, self.get_events( context ) )

class SharedMusicEvents():
    def __init__ ( self, context, node ):
        self.context = context
        self.node = node

    def get_events ( self, context ):
        forked = self.context.fork( cursor = context.cursor )

        for event in self.node.eval( forked ):
            context.join( forked )
            
            yield event

        context.join( forked )
        
