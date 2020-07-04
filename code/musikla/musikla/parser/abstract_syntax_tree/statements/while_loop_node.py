from typing import Tuple
from musikla.parser.printer import CodePrinter
from musikla.core import Context
from ..node import Node
from ..music_node import MusicSequenceBase

class WhileLoopStatementNode( MusicSequenceBase ):
    def __init__ ( self, condition : Node, body : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.condition : Node = condition
        self.body : Node = body

    def values ( self, context : Context ):
        condition_value = self.condition.eval( context )

        while condition_value:
            forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

            yield self.body.eval( forked )

            context.join( forked )

            condition_value = self.condition.eval( context )

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'while ' )

        with printer.block( '(', ')' ):
            self.condition.to_source( printer )

        with printer.block():
            self.body.to_source( printer )
