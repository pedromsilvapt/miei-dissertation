from musikla.parser.printer import CodePrinter
from musikla.core.events.event import MusicEvent
from musikla.core import Context, Library, CallableValue, Voice, Instrument, Music, Value, Ref
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core.events import ControlChangeEvent
from musikla.core.theory import Interval, Scale
from musikla.parser import Parser
from musikla.parser.abstract_syntax_tree import Node, MusicSequenceNode
from musikla.parser.abstract_syntax_tree.expressions import VariableExpressionNode
from typing import Any, Union
from fractions import Fraction

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

def function_ast_to_code ( ast : Node, ident = 4 ) -> str:
    printer = CodePrinter( ident = ident )

    return printer.print( ast )

def function_parse ( code : str ) -> Node:
    return Parser().parse( code )

def function_eval ( context : Context, code : Union[Node, str] ) -> Any:
    if type( code ) is str:
        code = function_parse( code )
    
    return Value.assignment( Value.eval( context, code ) )

def function_bool ( val ): return bool( val )

def function_int ( val ): return int( val )

def function_float ( val ): return float( val )

def function_str ( val ): return str( val )

def function_ord ( val ): return ord( val )

def function_chr ( val ): return chr( val )

def function_setvar ( var : Ref, value ):
    var.set( Value.assignment( value ) )

def function_hasattr ( o, name : str ):
    return hasattr( o, name )

def function_getattr ( o, name : str, default : Any = None ):
    return getattr( o, name, default = default )

def function_setattr ( o, name : str, value : Any ):
    return setattr( o, name, value )

def function_cc ( context : Context, control : int, value : int ):
    event = ControlChangeEvent( context.cursor, context.voice, control, value )
    
    return Music( [ event ] )

def function_gettime ( context : Context ):
    return context.cursor

def function_settime ( context : Context, time : int ):
    context.cursor = time

def function_slice ( notes : Music, start : int, end : int ):
    return notes.filter( lambda n: n.timestamp >= start and n.timestamp <= end )

def function_setvoice ( context : Context, voice : Voice ):
    context.voice = voice

def function_setinstrument ( context : Context, instrument : int ):
    context.voice = context.voice.clone( instrument = Instrument( "", instrument ) )

def function_debug ( context : Context, expr ):
    value = expr.eval( context.fork() )

    if value is None:
        print( None )
    elif isinstance( value, Music ):
        print( '<Music> ' + ' '.join( str( event ) for event in value.expand( context ) ) )
    else:
        print( "<%s>%s" % ( Value.typeof( value ), value ) )

def function_mod ( n : float, d : float ) -> float: 
    return n % d

def function_div ( n : float, d : float ) -> float: 
    return n // d

def function_inspect_context ( context : Context, ignore_root : bool = True ):
    symbols = context.symbols
    
    while symbols != None and ( not ignore_root or symbols.parent is not None ):
        print( f"Context#{ id( symbols ) } (Opaque = { symbols.opaque })" )
        for container_name, container in symbols.symbols.items():
            print( f"  - { container_name or '<default>' }:" )
            for key, value in container.items():
                print( f"    - { key }: { value }" )

        symbols = symbols.parent
    print()

def function_import ( context : Context, file : Node ):
    file_value : Value = file.eval( context )

    Value.expect( file, str, "Import" )

    ast = Parser().parse_file( file_value )

    return ast.eval( context )

def function_voices_create ( context : Context, name : str, modifiers : Node = None, inherit : Voice = None ):
    if inherit != None:
        pass

    voice = Voice( name, Instrument( name, 1 ) )

    if inherit != None:
        voice.instrument = inherit.instrument
        voice.time_signature = inherit.time_signature
        voice.velocity = inherit.velocity
        voice.octave = inherit.octave
        voice.value = inherit.value
        voice.tempo = inherit.tempo
    
    if modifiers != None:
        if isinstance( modifiers, MusicSequenceNode ):
            for modifier in modifiers:
                modifier.apply( voice )
        else:
            modifiers.apply( voice )

    return voice

def function_seek ( context : Context, time : Node ):
    context.cursor += Value.eval( context, time )

def function_len ( context : Context, obj : Any ):
    if isinstance( obj, Music ):
        return obj.len( context )
    else:
        return len( obj )

def function_stretch ( context : Context, music : Music, length_or_music : Union[Music, float, Fraction] ):
    new_length : Fraction = Fraction( 0 )

    if type( length_or_music ) is float:
        new_length = Fraction( length_or_music )
    elif isinstance( length_or_music, Music ):
        new_length = length_or_music.len( context )
    else:
        new_length = length_or_music
    
    music = music.shared()

    old_length = music.len( context )

    factor = new_length / old_length

    def _stretch ( event : MusicEvent, index : int, start_time : int ):
        nonlocal factor

        timestamp = int( ( event.timestamp - start_time ) * factor )

        return event.clone(
            timestamp = timestamp,
            value = event.value * factor,
            duration = context.voice.get_duration_absolute( event.value * factor )
        )

    return music.map( _stretch )

class StandardLibrary(Library):
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( "print", CallablePythonValue( print ) )
        context.symbols.assign( "debug", CallableValue( function_debug ) )
        context.symbols.assign( "discard", CallableValue( function_discard ) )
        context.symbols.assign( "play", CallableValue( function_play ) )
        context.symbols.assign( "using", CallableValue( function_using ) )
        context.symbols.assign( "import", CallableValue( function_import ) )
        context.symbols.assign( "seek", CallableValue( function_seek ) )
        context.symbols.assign( "ast", CallableValue( function_ast ) )
        context.symbols.assign( "ast_to_code", CallableValue( function_ast_to_code ) )
        context.symbols.assign( "parse", CallableValue( function_parse ) )
        context.symbols.assign( "eval", CallableValue( eval ) )

        context.symbols.assign( "bool", CallableValue( function_bool ) )
        context.symbols.assign( "int", CallablePythonValue( function_int ) )
        context.symbols.assign( "float", CallableValue( function_float ) )
        context.symbols.assign( "str", CallableValue( function_str ) )
        context.symbols.assign( "list", list )
        context.symbols.assign( "dict", dict )
        context.symbols.assign( "range", range )
        context.symbols.assign( "len", CallablePythonValue( function_len ) )

        context.symbols.assign( "mod", CallablePythonValue( function_mod ) )
        context.symbols.assign( "div", CallablePythonValue( function_div ) )

        context.symbols.assign( "inspect_context", CallablePythonValue( function_inspect_context ) )
        context.symbols.assign( "ord", CallableValue( function_ord ) )
        context.symbols.assign( "chr", CallableValue( function_chr ) )
        context.symbols.assign( "setvar", CallablePythonValue( function_setvar ) )
        context.symbols.assign( "hasattr", CallablePythonValue( function_hasattr ) )
        context.symbols.assign( "getattr", CallablePythonValue( function_getattr ) )
        context.symbols.assign( "setattr", CallablePythonValue( function_setattr ) )
        context.symbols.assign( "gettime", CallablePythonValue( function_gettime ) )
        context.symbols.assign( "settime", CallablePythonValue( function_settime ) )
        context.symbols.assign( "cc", CallablePythonValue( function_cc ) )
        context.symbols.assign( "setvoice", CallablePythonValue( function_setvoice ) )
        context.symbols.assign( "setinstrument", CallablePythonValue( function_setinstrument ) )
        context.symbols.assign( "interval", Interval )
        context.symbols.assign( "scale", Scale )

        context.symbols.assign( "stretch", CallablePythonValue( function_stretch ) )

        context.symbols.assign( "voices\\create", CallablePythonValue( function_voices_create ) )
