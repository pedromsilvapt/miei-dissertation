from musikla.parser.printer import CodePrinter
from musikla.core import Context, SymbolsScope, CallableValue, Value
from .statement_node import StatementNode
from ..expressions import VariableExpressionNode
from ..stack_frame_node import StackFrameNode
from typing import Tuple

class FunctionDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, arguments, body, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.name = name
        self.arguments = arguments
        self.body = StackFrameNode( body, position = position )

    def __eval__ ( self, context : Context ):
        fn = CallableValue( lambda *args, **kargs: self.exec( context.symbols, *args, **kargs ) )

        if self.name != None:
            context.symbols.assign( self.name, fn )

        return fn

    def exec ( self, symbols_scope : SymbolsScope, context : Context, *args, **kargs ):
        forked = context.fork( symbols = symbols_scope.fork() )

        for i in range( len( self.arguments ) ):
            ( name, arg_mod, default_value ) = self.arguments[ i ]

            arg_context = context
            is_provided : bool = True
            
            if len( args ) > i:
                node = args[ i ]
            elif name in kargs:
                node = kargs[ name ]
            elif default_value != None:
                node = default_value
                arg_context = forked
                is_provided = False
            else:
                raise Exception( f"Mandatory argument { name } was not given." )

            if arg_mod == 'expr':
                forked.symbols.assign( name, node )
            elif arg_mod == 'ref' and is_provided:
                if not isinstance( node, VariableExpressionNode ):
                    raise BaseException( f"Only variable references can be passed to a function (function { self.name }, parameter { name })" )
                
                forked.symbols.using( context.symbols.pointer( node.name ), name )
            elif arg_mod == 'in' and is_provided:
                if is_provided and isinstance( node, VariableExpressionNode ):
                    forked.symbols.using( context.symbols.pointer( node.name ), name )
                else:
                    forked.symbols.assign( name, Value.assignment( node.eval( arg_context.fork() ) ) )
            else:
                forked.symbols.assign( name, Value.assignment( node.eval( arg_context.fork() ) ) )

        return self.body.eval( forked )
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'fun ' )

        if self.name is not None:
            printer.add_token( self.name + ' ' )

        printer.begin_block( '(', ')' )

        for i in range( len( self.arguments ) ):
            if i > 0:
                printer.add_token( ', ' )

            name, mod, expr = self.arguments[ i ]

            if mod is not None:
                printer.add_token( mod + ' ' )
            
            printer.add_token( '$' + name )

            if expr is not None:
                printer.add_token( ' = ' )

                expr.to_source( printer )

        printer.end_block()

        printer.begin_block()

        self.body.to_source( printer )

        printer.end_block()
