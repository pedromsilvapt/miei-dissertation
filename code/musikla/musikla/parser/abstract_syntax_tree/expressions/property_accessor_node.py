from typing import Tuple
from musikla.core import Context, Value, Music
from ..node import Node

class PropertyAccessorNode( Node ):
    def __init__ ( self, expression : Node, name : Node, position : Tuple[int, int] = None ):
        super().__init__( position )
        
        self.expression : Node = expression
        self.name : Node = name

    def get_events ( self, context : Context, forked : Context, value : Value ):
        try:
            for event in value.expand( context ):
                yield event
        finally:
            context.join( forked )

    def eval ( self, context : Context, assignment : bool = False ):
        expr = self.expression.eval( context )
        name = self.name.eval( context )

        if type( name ) is int:
            return expr[ name ]
        else:
            return getattr( expr, name, None )

