from core import Context, SymbolsScope, CallableValue
from .statement_node import StatementNode
from ..expressions import VariableExpressionNode

class FunctionDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, arguments, body, position : (int, int) = None ):
        super().__init__( position )

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
            ( name, arg_mod ) = self.arguments[ i ]

            node = args[ i ]

            if arg_mod == 'expr':
                forked.symbols.assign( name, node )
            elif arg_mod == 'ref':
                if not isinstance( node, VariableExpressionNode ):
                    raise BaseException( f"Only variable references can be passed to a function (function { self.name }, parameter { name })" )

                forked.symbols.using( context.symbols.pointer( node.name ), name )
            else:
                forked.symbols.assign( name, node.eval( context, assignment = True ) )
        
        return self.body.eval( forked )
