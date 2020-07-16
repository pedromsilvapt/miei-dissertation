from musikla.parser.printer import CodePrinter
from .expression_node import ExpressionNode
from typing import List, Tuple
from musikla.core import Value

class ArrayLiteralNode( ExpressionNode ):
    def __init__ ( self, values : List[ExpressionNode], position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.values : List[ExpressionNode] = values

    def __eval__ ( self, context ):
        return [ Value.assignment( Value.eval( context.fork(), node ) ) for node in self.values ]

    def to_source ( self, printer : CodePrinter ):
        with printer.block( '@[', ']' ):
            for i in range( len( self.values ) ):
                if i > 0:
                    printer.add_token( '; ' )
                
                self.values[ i ].to_source( printer )
