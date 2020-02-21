from musikla.core import Context, SymbolsScope, CallableValue, Value
from .statement_node import StatementNode
from ..expressions import VariableExpressionNode

class FunctionDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, arguments, body, position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.arguments = arguments
        self.body = body

    def eval ( self, context : Context ):
        fn = CallableValue( lambda *args, **kargs: self.exec( context.symbols, *args, **kargs ) )

        if self.name != None:
            context.symbols.assign( self.name, fn )

        return fn

    def exec ( self, symbols_scope : SymbolsScope, context : Context, *args, **kargs ):
        forked = context.fork( symbols = symbols_scope.fork() )

        for i in range( len( self.arguments ) ):
            ( name, arg_mod, default_value ) = self.arguments[ i ]

            arg_context = context
            
            if len( args ) > i:
                node = args[ i ]
            elif name in kargs:
                node = kargs[ name ]
            elif default_value != None:
                node = default_value
                arg_context = forked
            else:
                raise Exception( f"Mandatory argument { name } was not given." )

            if arg_mod == 'expr':
                forked.symbols.assign( name, node )
            elif arg_mod == 'ref':
                if not isinstance( node, VariableExpressionNode ):
                    raise BaseException( f"Only variable references can be passed to a function (function { self.name }, parameter { name })" )

                forked.symbols.using( context.symbols.pointer( node.name ), name )
            else:
                forked.symbols.assign( name, Value.assignment( node.eval( arg_context.fork() ) ) )

        return self.body.eval( forked )
