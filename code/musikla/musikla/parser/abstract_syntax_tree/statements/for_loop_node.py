from musikla.parser.printer import CodePrinter
from typing import List, Tuple
from musikla.core import Value
from ..node import Node
from ..music_node import MusicSequenceBase

class ForLoopStatementNode( MusicSequenceBase ):
    def __init__ ( self, variable : List[str], it : Node, body : Node, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.variables : List[str] = variable
        self.it : Node = it
        self.body : Node = body

    def values ( self, context ):
        for i in Value.eval( context, self.it ):
            forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

            if len( self.variables ) == 1:
                forked.symbols.assign( self.variables[ 0 ], i, local = True )
            else:
                for k, name in enumerate( self.variables ):
                    forked.symbols.assign( name, i[ k ], local = True )

            yield Value.eval( forked, self.body )

            context.join( forked )

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'for ' )

        with printer.block( '(', ')' ):
            printer.add_token( ", ".join( [ "$" + name for name in self.variables ] ) + " in " )
            
            self.it.to_source( printer )

        with printer.block():
            self.body.to_source( printer )
