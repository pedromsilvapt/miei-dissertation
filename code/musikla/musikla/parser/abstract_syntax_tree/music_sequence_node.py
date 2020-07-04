from musikla.parser.printer import CodePrinter
from typing import Tuple
from .music_node import MusicSequenceBase

class MusicSequenceNode( MusicSequenceBase ):
    def __init__ ( self, nodes, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.expressions = nodes

    def to_source ( self, printer : CodePrinter ):
        for i in range( len( self.expressions ) ):
            if i > 0: printer.add_token( ' ' )

            self.expressions[ i ].to_source( printer )

    def values ( self, context ):
        for node in self.expressions:
            yield node.eval( context )

    def __iter__ ( self ):
        return iter( self.expressions )
