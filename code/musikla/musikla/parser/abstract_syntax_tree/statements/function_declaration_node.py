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

        forked.symbols.assign( '__callerctx__', context, local = True )

        for i in range( len( self.arguments ) ):
            ( name, arg_mod, default_value ) = self.arguments[ i ]

            argument_node, default_node = None, default_value

            if len( args ) > i:
                argument_node = args[ i ]
            elif name in kargs:
                argument_node = kargs[ name ]
            elif default_value == None:
                raise Exception( f"Mandatory argument { name } was not given." )

            if arg_mod == 'expr':
                forked.symbols.assign( name, argument_node )
            elif ( arg_mod == 'ref' or arg_mod == 'in' ) and argument_node is not None:
                is_variable = isinstance( argument_node, VariableExpressionNode )

                if arg_mod == 'ref' and not is_variable:
                    raise BaseException( f"Only variable references can be passed to a function (function { self.name }, parameter { name })" )

                # TODO: Should ref pointers be shallow? Since ref can mutate
                # the value, it could be sensible for them to be so
                if is_variable:
                    pointer = context.symbols.pointer( argument_node.name )

                    if pointer is None:
                        context.symbols.assign( argument_node.name, None )
                    else:
                        forked.symbols.using( pointer, name )
                else:
                    forked.symbols.assign( name, Value.assignment( argument_node.eval( context.fork() ) ) )
            else:
                if argument_node is not None:
                    value = Value.assignment( argument_node.eval( context.fork() ) )
                else:
                    value = Value.assignment( default_node.eval( forked.fork() ) )
                
                value = forked.symbols.assign( name, value )

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
