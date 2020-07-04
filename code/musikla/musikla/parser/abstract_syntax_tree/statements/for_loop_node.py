from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Value
from ..node import Node
from ..music_node import MusicSequenceBase

class ForLoopStatementNode( MusicSequenceBase ):
    def __init__ ( self, variable : str, it : Node, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.variable : str = variable
        self.it : Node = it
        self.body : Node = body

    def values ( self, context ):
        for i in Value.eval( context, self.it ):
            forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

            forked.symbols.assign( self.variable, i, local = True )

            yield Value.eval( forked, self.body )

            context.join( forked )

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'for ' )

        with printer.block( '(', ')' ):
            printer.add_token( "$" + self.variable + " in " )

            self.it.to_source( printer )

        with printer.block():
            self.body.to_source( printer )
