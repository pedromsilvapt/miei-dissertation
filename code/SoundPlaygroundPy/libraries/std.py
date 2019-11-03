from core import Context, Library, CallableValue
from core import Value, VALUE_KIND_MUSIC, VALUE_KIND_STRING
from parser import Parser
from parser.abstract_syntax_tree import Node
from parser.abstract_syntax_tree.expressions import VariableExpressionNode

def function_using ( context : Context, var ):
    if not isinstance( var, VariableExpressionNode ):
        raise BaseException( f"Using expected a variable syntax node" )

    context.symbols.using( var.name )

def function_play ( context : Context, expr ):
    value = expr.eval( context )

    if value and value.kind == VALUE_KIND_MUSIC:
        return value

    return Value( VALUE_KIND_MUSIC, iter(()) )

def function_discard ( context : Context, expr ):
    expr.eval( context.fork() )

    return None

def function_debug ( context : Context, expr ):
    value = expr.eval( context.fork() )

    if value == None:
        print( None )
    elif value.kind == VALUE_KIND_MUSIC:
        print( '<Music> ' + ' '.join( str( event ) for event in value ) )
    else:
        print( "<%s>%s" % ( value.kind, value.value ) )

def function_import ( context : Context, file : Node ):
    file_value : Value = file.eval( context )

    if file_value == None or file_value.kind != VALUE_KIND_STRING:
        raise BaseException( 'Expected string in import function.' )

    ast = Parser().parse_file( file_value.value )

    return ast.eval( context )

class StandardLibrary(Library):
    def on_link ( self ):
        context : Context = self.context

        context.symbols.assign( "debug", CallableValue( function_debug ) )
        context.symbols.assign( "discard", CallableValue( function_discard ) )
        context.symbols.assign( "play", CallableValue( function_play ) )
        context.symbols.assign( "using", CallableValue( function_using ) )
        context.symbols.assign( "import", CallableValue( function_import ) )

