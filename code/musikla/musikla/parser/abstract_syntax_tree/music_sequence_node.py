from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Value, Music
from .music_node import MusicNode

class MusicSequenceNode( MusicNode ):
    def __init__ ( self, nodes, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.expressions = nodes

    def to_source ( self, printer : CodePrinter ):
        for i in range( len( self.expressions ) ):
            if i > 0: printer.add_token( ' ' )

            self.expressions[ i ].to_source( printer )

    def get_events ( self, context ):
        for node in self.expressions:
            value = node.eval( context )

            if isinstance( value, Music ):
                for event in value.expand( context ):
                    yield event

                    if event.end_timestamp > context.cursor:
                        context.cursor = event.end_timestamp
    
    def __iter__ ( self ):
        return iter( self.expressions )
