from musikla.parser.printer import CodePrinter
from typing import Tuple
from ..node import Node
from .expression_node import ExpressionNode
from musikla.core import Context

class UnaryOperatorNode( ExpressionNode ):
    def __init__ ( self, node : Node, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.node : Node = node

    def __eval__ ( self, context, assignment : bool = False ):
        return None

class NotOperatorNode ( UnaryOperatorNode ):
    def __eval__ ( self, context : Context, assignment : bool = False ):
        value = self.node.eval( context )

        return not bool( value )
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( "not " )

        self.node.to_source( printer )
