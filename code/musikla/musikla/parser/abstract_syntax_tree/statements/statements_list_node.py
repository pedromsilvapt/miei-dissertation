from typing import Tuple
from ..music_node import MusicSequenceBase
from musikla.parser.printer import CodePrinter

class StatementsListNode( MusicSequenceBase ):
    def __init__ ( self, nodes, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.statements = nodes

    def to_source ( self, printer : CodePrinter ):
        for i in range( len( self.statements ) ):
            if i > 0:
                printer.add_token( ';' )
            
            printer.begin_line()

            self.statements[ i ].to_source( printer )

    def values ( self, context ):
        for node in self.statements:
            yield node.eval( context )
