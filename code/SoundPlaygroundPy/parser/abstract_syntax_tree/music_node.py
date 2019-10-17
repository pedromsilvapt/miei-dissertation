from .expressions import ExpressionNode
from core import Value, VALUE_KIND_MUSIC

class MusicNode( ExpressionNode ):
    def __init__ ( self ):
        super().__init__()
    
    def as_assignment ( self, context ):
        return Value( VALUE_KIND_MUSIC, SharedMusicEvents( context.fork(), self ) )

    def get_events ( self, context ):
        return iter( () )

# class SharedIterator():
#     def __init__ ( self, iterator ):
#         self.iterator = iterator
#         self.cursor = IterCursor( self.iterator )
#         self.buffer = list()

#     def __iter__ ():
#         index = 0

#         while not self.cursor.ended:
#             if index <= len( self.buffer ):
#                 if self.cursor.move_next():
#                     self.buffer.append( self.cursor.current )
#                 else:
#                     break

#             yield self.buffer[ index ]

#             index += 1


class SharedMusicEvents():
    def __init__ ( self, context, node ):
        self.context = context
        self.node = node

    def get_events ( self, context ):
        forked = self.context.fork( cursor = context.cursor )

        for event in self.node.get_events( forked ):
            
            context.join( forked )
            
            yield event

        context.join( forked )
        
