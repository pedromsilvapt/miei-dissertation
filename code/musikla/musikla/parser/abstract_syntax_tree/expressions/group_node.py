from typing import Tuple
from musikla.parser.printer import CodePrinter
from musikla.core import Context, Music
from ..node import Node

class GroupNode( Node ):
    def __init__ ( self, expression, position : Tuple[int, int] = None ):
        super().__init__( position )
        
        self.expression = expression

    def get_events ( self, context : Context, forked : Context, value : Music ):
        try:
            for event in value.expand( context ):
                yield event
        finally:
            context.join( forked )

    def eval ( self, context : Context, assignment : bool = False ):
        forked = context.fork()

        value = self.expression.eval( forked )

        if isinstance( value, Music ):
            return Music( self.get_events( context, forked, value ) )
        else:
            context.join( forked )

            return value

    def to_source ( self, printer : CodePrinter ):
        with printer.block( '(', ')' ):
            self.expression.to_source( printer )

