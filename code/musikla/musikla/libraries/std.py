from musikla.parser.printer import CodePrinter
from musikla.core.events.event import MusicEvent
from musikla.core import Context, Library, CallableValue, Voice, Instrument, Music, Value, Ref
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core.events import ControlChangeEvent
from musikla.core.theory import Interval, Scale
from musikla.parser import Parser
from musikla.parser.abstract_syntax_tree import Node, MusicSequenceNode
from musikla.parser.abstract_syntax_tree.expressions import VariableExpressionNode
from musikla.audio.sequencers.sequencer import Sequencer
from musikla.audio import Player
from typing import Any, List, Union, cast
from fractions import Fraction
import musikla.audio.sequencers as seqs

def function_getctx ( context : Context ):
    return context

def function_withctx( _ : Context, ctx : Context, expr : Node ):
    return Value.eval( ctx, expr )

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

def function_eval ( context : Context, code ) -> Any:
    if type( code ) is str:
        code = function_parse( code )
    
    return Value.assignment( Value.eval( context, code ) )

SequencerLike = Union[str, List[str], Sequencer]

def function_make_sequencer ( context : Context, sequencer : SequencerLike ) -> Sequencer:
    std = cast( StandardLibrary, context.library( StandardLibrary ) )

    format = None
    uri = None
    args = None

    if type(sequencer) is str:
        uri = sequencer
    elif type( sequencer ) is list:
        args_start = 0

        if len( sequencer ) >= args_start + 2 and sequencer[ args_start ] == '-o':
            uri = sequencer[ args_start + 1 ]
            args_start += 2

        if len( sequencer ) >= args_start + 2 and sequencer[ args_start ] == '-f':
            format = sequencer[ args_start + 1 ]
            args_start += 2

        args = sequencer[ args_start: ]
    elif isinstance( sequencer, Sequencer ):
        return sequencer

    if format is not None:
        return std.player.make_sequencer_from_format( format, uri or "", args or [] )
    
    return std.player.make_sequencer_from_uri( uri or "", args or [] )

def function_save ( context : Context, music : Music, outputs : Union[str, Sequencer, List[SequencerLike]] ) -> Any:
    # The single parameter specifies if only one sequencer was given
    # In that case, instead of returning an array, we return just the sequencer
    single : bool = False

    if type( outputs ) is str or isinstance( outputs, Sequencer ):
        sequencers : List[Sequencer] = [ function_make_sequencer( context, outputs ) ]

        single = True
    else:
        sequencers : List[Sequencer] = [ function_make_sequencer( context, seq ) for seq in outputs ]

    for seq in sequencers: 
        seq.realtime = False

        seq.start()

    for ev in music.expand( context.fork( cursor = 0 ) ):
        for seq in sequencers:
            seq.register_event( ev )

    for seq in sequencers: seq.close()

    if single:
        return sequencers[ 0 ]

    return sequencers

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
    def __init__ ( self, player : Player ):
        super().__init__()

        self.player : Player = player
    
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( "getctx", CallablePythonValue( function_getctx ) )
        context.symbols.assign( "withctx", CallablePythonValue( function_withctx ) )
        context.symbols.assign( "print", CallablePythonValue( print ) )
        context.symbols.assign( "debug", CallableValue( function_debug ) )
        context.symbols.assign( "discard", CallableValue( function_discard ) )
        context.symbols.assign( "play", CallableValue( function_play ) )
        context.symbols.assign( "using", CallableValue( function_using ) )
        context.symbols.assign( "import", CallableValue( function_import ) )
        context.symbols.assign( "seek", CallableValue( function_seek ) )
        context.symbols.assign( "ast", CallableValue( function_ast ) )
        context.symbols.assign( "ast_to_code", CallablePythonValue( function_ast_to_code ) )
        context.symbols.assign( "parse", CallablePythonValue( function_parse ) )
        context.symbols.assign( "eval", CallablePythonValue( function_eval ) )
        context.symbols.assign( "make_sequencer", CallablePythonValue( function_make_sequencer ) )
        context.symbols.assign( "save", CallablePythonValue( function_save ) )

        context.symbols.assign( "bool", CallablePythonValue( function_bool ) )
        context.symbols.assign( "int", CallablePythonValue( function_int ) )
        context.symbols.assign( "float", CallablePythonValue( function_float ) )
        context.symbols.assign( "str", CallablePythonValue( function_str ) )
        context.symbols.assign( "list", list )
        context.symbols.assign( "dict", dict )
        context.symbols.assign( "range", range )
        context.symbols.assign( "len", CallablePythonValue( function_len ) )

        context.symbols.assign( "mod", CallablePythonValue( function_mod ) )
        context.symbols.assign( "div", CallablePythonValue( function_div ) )

        context.symbols.assign( "inspect_context", CallablePythonValue( function_inspect_context ) )
        context.symbols.assign( "ord", CallablePythonValue( function_ord ) )
        context.symbols.assign( "chr", CallablePythonValue( function_chr ) )
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

        context.symbols.assign( "sequencers\\ABC", CallablePythonValue( seqs.ABCSequencer ) )
        context.symbols.assign( "sequencers\\PDF", CallablePythonValue( seqs.PDFSequencer ) )
        context.symbols.assign( "sequencers\\HTML", CallablePythonValue( seqs.HTMLSequencer ) )
        context.symbols.assign( "sequencers\\Midi", CallablePythonValue( seqs.MidiSequencer ) )
        context.symbols.assign( "sequencers\\Debug", CallablePythonValue( seqs.DebugSequencer ) )
        context.symbols.assign( "sequencers\\FluidSynth", CallablePythonValue( seqs.FluidSynthSequencer ) )

        context.symbols.assign( "voices\\create", CallablePythonValue( function_voices_create ) )
