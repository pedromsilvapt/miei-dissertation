from core import Context, SymbolsScope, Value
from ..node import Node
from .statement_node import StatementNode

class ForLoopStatementNode( StatementNode ):
    def __init__ ( self, variable : str, min : Node, max : Node, body : Node, position : (int, int) = None ):
        super().__init__( position )

        self.variable : str = variable
        self.min : Node = min
        self.max : Node = max
        self.body : Node = body

    def eval ( self, context : Context ):
        min_value = self.min.eval( context )

        Value.expect( min_value, float, "For loop minimum" )
        
        max_value = self.max.eval( context )

        Value.expect( max_value, float, "For loop maximum" )

        result = None

        # TODO Study creating a custom scope for this loop
        forked = context.fork( symbols = context.symbols.fork( opaque = False ) )
        for i in range( min_value.value, max_value.value ):
            forked.symbols.assign( self.variable, i, local = True )

            result = self.body.eval( forked )
            
        return result

