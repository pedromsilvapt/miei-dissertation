from core import Context, Library, CallableValue, Voice, Instrument, Music, Value
from core.callable_python_value import CallablePythonValue
from core.events import ControlChangeEvent
from parser import Parser
from parser.abstract_syntax_tree import Node, MusicSequenceNode
from parser.abstract_syntax_tree.expressions import VariableExpressionNode

def function_using ( context : Context, var ):
    if not isinstance( var, VariableExpressionNode ):
        raise BaseException( f"Using expected a variable syntax node" )

    context.symbols.using( var.name )

def function_play ( context : Context, expr ):
    value = expr.eval( context )

    if isinstance( value, Music ):
        return value

    return Music()

def function_discard ( context : Context, *expr ):
    for e in expr:
        e.eval( context.fork() )

    return None

def function_ast ( context : Context, expr ):
    return expr


def function_bool ( val ): return bool( val )

def function_int ( val ): return int( val )

def function_float ( val ): return float( val )

def function_str ( val ): return str( val )

def function_ord ( val ): return ord( val )

def function_chr ( val ): return chr( val )

def function_cc ( context : Context, control : int, value : int ):
    event = ControlChangeEvent( context.cursor, context.voice, control, value )
    
    return Music( [ event ] )

def function_debug ( context : Context, expr ):
    value = expr.eval( context.fork() )

    if value == None:
        print( None )
    elif isinstance( value, Music ):
        print( '<Music> ' + ' '.join( str( event ) for event in value ) )
    else:
        print( "<%s>%s" % ( Value.typeof( value ), value ) )

def function_import ( context : Context, file : Node ):
    file_value : Value = file.eval( context )

    Value.expect( file, str, "Import" )

    ast = Parser().parse_file( file_value )

    return ast.eval( context )

def function_voices_create ( context : Context, name : str, instrument : int = None, modifiers : Node = None, inherit : Voice = None ):
    if inherit != None:
        pass

    voice = Voice( name, Instrument( name, 1 if instrument is None else instrument ) )

    if inherit != None:
        if instrument is None:
            voice.instrument = inherit.instrument

        voice.time_signature = inherit.time_signature
        voice.velocity = inherit.velocity
        voice.octave = inherit.octave
        voice.value = inherit.value
        voice.tempo = inherit.tempo
    
    if modifiers != None:
        # Value.expect( modifiers, MusicSequenceNode )

        if isinstance( modifiers, MusicSequenceNode ):
            for modifier in modifiers:
                modifier.apply( voice )
        else:
            modifiers.apply( voice )

    return voice

class StandardLibrary(Library):
    def on_link ( self ):
        context : Context = self.context

        context.symbols.assign( "debug", CallableValue( function_debug ) )
        context.symbols.assign( "discard", CallableValue( function_discard ) )
        context.symbols.assign( "play", CallableValue( function_play ) )
        context.symbols.assign( "using", CallableValue( function_using ) )
        context.symbols.assign( "import", CallableValue( function_import ) )
        context.symbols.assign( "ast", CallableValue( function_ast ) )

        context.symbols.assign( "bool", CallableValue( function_bool ) )
        context.symbols.assign( "int", CallablePythonValue( function_int ) )
        context.symbols.assign( "float", CallableValue( function_float ) )
        context.symbols.assign( "str", CallableValue( function_str ) )

        context.symbols.assign( "ord", CallableValue( function_ord ) )
        context.symbols.assign( "chr", CallableValue( function_chr ) )
        context.symbols.assign( "cc", CallablePythonValue( function_cc ) )

        context.symbols.assign( "voices\\create", CallablePythonValue( function_voices_create ) )
