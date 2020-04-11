from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Context, SymbolsScope, Value
from ..node import Node
from .statement_node import StatementNode

class ForLoopStatementNode( StatementNode ):
    def __init__ ( self, variable : str, it : Node, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.variable : str = variable
        self.it : Node = it
        self.body : Node = body

    def eval ( self, context : Context ):
        result = None

        for i in Value.eval( context.fork(), self.it ):
            forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

            forked.symbols.assign( self.variable, i, local = True )

            result = Value.eval( forked, self.body )
            
        return result

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'for ' )

        with printer.block( '(', ')' ):
            printer.add_token( "$" + self.variable + " in " )

            self.it.to_source( printer )

        with printer.block():
            self.body.to_source( printer )
