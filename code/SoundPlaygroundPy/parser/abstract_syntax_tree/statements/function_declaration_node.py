from core import Context, SymbolsScope, CallableValue
from .statement_node import StatementNode

class FunctionDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, arguments, body ):
        super().__init__()

        self.name = name
        self.arguments = arguments
        self.body = body

    def eval ( self, context : Context, assignment : bool = False ):
        fn = CallableValue( lambda *args: self.exec( context.symbols, *args ) )

        context.symbols.assign( self.name, fn )

        return None

    def exec ( self, symbols_scope : SymbolsScope, context : Context, *args ):
        forked = context.fork( symbols = symbols_scope.fork() )

        for i in range( len( self.arguments ) ):
            ( name, is_expr ) = self.arguments[ i ]

            node = args[ i ]

            if is_expr:
                forked.symbols.assign( name, node )
            else:
                forked.symbols.assign( name, node.eval( context, assignment = True ) )
        
        return self.body.eval( forked )
