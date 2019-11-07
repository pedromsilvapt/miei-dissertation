from core import Context, SymbolsScope, Value, VALUE_KIND_NUMBER
from ..node import Node
from .statement_node import StatementNode

class ForLoopStatementNode( StatementNode ):
    def __init__ ( self, variable : str, min : Node, max : Node, body : Node, position : (int, int) = None ):
        super().__init__( position )

        self.variable : str = variable
        self.min : Node = min
        self.max : Node = max
        self.body : Node = body

    def eval ( self, context : Context, assignment : bool = False ):
        min_value : Value = self.min.eval( context )

        if min_value.kind != VALUE_KIND_NUMBER:
            raise BaseException( "For loop minimum value expected a number, got %s" % min_value.kind )
        
        max_value : Value = self.max.eval( context )

        if max_value.kind != VALUE_KIND_NUMBER:
            raise BaseException( "For loop maximum value expected a number, got %s" % max_value.kind )

        result = None

        # TODO Study creating a custom scope for this loop
        forked = context.fork( symbols = context.symbols.fork( opaque = False ) )
        for i in range( min_value.value, max_value.value ):
            forked.symbols.assign( self.variable, Value( VALUE_KIND_NUMBER, i ), local = True )

            result = self.body.eval( forked )
            
        return result

