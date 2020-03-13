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
        # Value.expect( min_value, float, "For loop minimum" )
        # Value.expect( max_value, float, "For loop maximum" )

        result = None

        # TODO Study creating a custom scope for this loop
        for i in Value.eval( context.fork(), self.it ):
            forked = context.fork( symbols = context.symbols.fork( opaque = False ) )

            forked.symbols.assign( self.variable, i, local = True )

            result = Value.eval( forked, self.body )
            
        return result

