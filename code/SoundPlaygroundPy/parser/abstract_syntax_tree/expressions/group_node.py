from core import Context, Value
from ..node import Node

class GroupNode( Node ):
    def __init__ ( self, expression, position : (int, int) = None ):
        super().__init__( position )
        
        self.expression = expression

    def get_events ( self, context : Context, forked : Context, value : Value ):
        try:
            for event in value:
                yield event
        finally:
            context.join( forked )

    def eval ( self, context : Context, assignment : bool = False ):
        forked = context.fork()

        value : Value = self.expression.eval( forked )

        if value.is_music:
            return Value.create( self.get_events( context, forked, value ) )
        else:
            context.join( forked )

            return value

