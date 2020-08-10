from musikla.core.symbols_scope import Pointer
from musikla.parser.printer import CodePrinter
from musikla.core.events.event import MusicEvent
from musikla.core import Context, Library, CallableValue, Voice, Metronome, Instrument, Music, Value, Ref
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core.events import ControlChangeEvent
from musikla.core.theory import Interval, Scale
from musikla.parser import Parser
from musikla.parser.abstract_syntax_tree import Node, MusicSequenceNode
from musikla.parser.abstract_syntax_tree.expressions import VariableExpressionNode
from musikla.parser.abstract_syntax_tree.context_modifiers import ContextModifierNode
from musikla.audio.sequencers.sequencer import Sequencer
from musikla.audio import Player
from typing import Any, List, Union, cast
from pathlib import Path
from fractions import Fraction
import musikla.audio.sequencers as seqs

def function_getctx ( context : Context ):
    return context

def function_withctx( _ : Context, ctx : Context, expr : Node ):
    return Value.eval( ctx, expr )

def function_pack ( context : Context, into = None, ctx = None, prefix : str = None, exclude = None, ignore_existing = False ):
    ctx = ctx or context
    into = into or type('PackedObject', (object,), {})()

    for key, value in ctx.symbols.enumerate( local = True ):
        if not key.startswith( '_' ) and ( exclude is None or key not in exclude ):
            p_key = ( prefix or "" ) + key

            if hasattr( into, p_key ) and not ignore_existing:
                raise BaseException( f"pack(): Cannot pack attribute '{ p_key }' of '{ type(into) }', attribute already exists." )

            if isinstance( value, Pointer ):
                value = value.scope.lookup( value.name )

            setattr( into, p_key, value )
    
    return into

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
        value = e.eval( context.fork() )

        if isinstance(value, Music):
            for _ in value: pass

    return None

def function_ast ( context : Context, expr ):
    return expr

def function_ast_to_code ( ast : Node, ident = 4 ) -> str:
    printer = CodePrinter( ident = ident )

    return printer.print( ast )

def function_parse ( context : Context, code : str, rule : str = None ) -> Node:
    return context.script.parse( code, rule = rule )

def function_eval ( context : Context, code, rule : str = None ) -> Any:
    if type( code ) is str:
        code = function_parse( context, code, rule = rule )
    
    return Value.assignment( Value.eval( context, code ) )

def function_pyeval ( context : Context, code ) -> Any:
    from musikla.parser.abstract_syntax_tree.python_node import PythonNode
    
    return PythonNode.eval( context, code, True )

def function_pyexec ( context : Context, code ) -> Any:
    from musikla.parser.abstract_syntax_tree.python_node import PythonNode
    
    return PythonNode.execute( context, code, False )

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

def function_getcwd ():
    import os

    return os.getcwd()

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

def function_setinstrument ( context : Context, instrument : int, bank : int = None, soundfont : Union[int, str] = None ):
    context.voice.instrument = Instrument.from_program( instrument, bank, soundfont )

def function_sfload ( context : Context, soundfont : str, alias : str = None, only_new : bool = False ):
    script = context.script

    if not only_new:
        for seq in script.player.sequencers:
            if hasattr( seq, 'load_soundfont' ):
                cast( Any, seq ).load_soundfont( soundfont, alias )
    
    for factory in script.player.sequencer_factories:
        if hasattr( factory, 'add_soundfont' ):
            cast( Any, factory ).add_soundfont( soundfont, alias )

def function_sfunload ( context : Context, soundfont : str, only_new : bool = False ):
    script = context.script

    if not only_new:
        for seq in script.player.sequencers:
            if hasattr( seq, 'unload_soundfont' ):
                cast( Any, seq ).unload_soundfont( soundfont )
    
    for factory in script.player.sequencer_factories:
        if hasattr( factory, 'remove_soundfont' ):
            cast( Any, factory ).remove_soundfont( soundfont )

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

def function_inspect_context ( context : Context, ignore_root : bool = True, ignore_symbols : bool = False ):
    symbols = context.symbols
    
    while symbols != None and ( not ignore_root or symbols.parent is not None ):
        print( f"Context#{ id( symbols ) } (Opaque = { symbols.opaque })" )

        if not ignore_symbols:
            for container_name, container in symbols.symbols.items():
                print( f"  - { container_name or '<default>' }:" )
                for key, value in container.items():
                    print( f"    - { key }: { value }" )

        symbols = symbols.parent
    print()

def function_voices_create ( context : Context, name : str, modifiers : Node = None, inherit : Voice = None ):
    if inherit != None:
        pass

    voice = Voice( name, Instrument( name, 1 ) )
    forked = context.fork()
    forked.voice = voice

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
                if isinstance( modifier, ContextModifierNode ):
                    modifier.apply( voice )
                else:
                    modifier.eval( forked )
        else:
            if isinstance( modifiers, ContextModifierNode ):
                modifiers.apply( voice )
            else:
                modifiers.eval( forked )

    return voice

def function_seek ( context : Context, time : Node ):
    context.cursor += Value.eval( context, time )

def function_len ( context : Context, obj : Any ):
    if isinstance( obj, Music ):
        return obj.len( context )
    else:
        return len( obj )

class StandardLibrary(Library):
    def __init__ ( self, player : Player ):
        super().__init__()

        self.player : Player = player
    
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( "getctx", CallablePythonValue( function_getctx ) )
        context.symbols.assign( "withctx", CallablePythonValue( function_withctx ) )
        context.symbols.assign( "pack", CallablePythonValue( function_pack ) )
        context.symbols.assign( "print", CallablePythonValue( print ) )
        context.symbols.assign( "debug", CallableValue( function_debug ) )
        context.symbols.assign( "discard", CallableValue( function_discard ) )
        context.symbols.assign( "play", CallableValue( function_play ) )
        context.symbols.assign( "using", CallableValue( function_using ) )
        context.symbols.assign( "seek", CallableValue( function_seek ) )
        context.symbols.assign( "ast", CallableValue( function_ast ) )
        context.symbols.assign( "ast_to_code", CallablePythonValue( function_ast_to_code ) )
        context.symbols.assign( "parse", CallablePythonValue( function_parse ) )
        context.symbols.assign( "eval", CallablePythonValue( function_eval ) )
        context.symbols.assign( "pyeval", CallablePythonValue( function_pyeval ) )
        context.symbols.assign( "pyexec", CallablePythonValue( function_pyexec ) )
        context.symbols.assign( "make_sequencer", CallablePythonValue( function_make_sequencer ) )
        context.symbols.assign( "save", CallablePythonValue( function_save ) )
        context.symbols.assign( "getcwd", CallablePythonValue( function_getcwd ) )

        context.symbols.assign( "bool", CallablePythonValue( bool ) )
        context.symbols.assign( "int", CallablePythonValue( int ) )
        context.symbols.assign( "float", CallablePythonValue( float ) )
        context.symbols.assign( "str", CallablePythonValue( str ) )
        context.symbols.assign( "list", CallablePythonValue( list ) )
        context.symbols.assign( "dict", CallablePythonValue( dict ) )
        context.symbols.assign( "range", CallablePythonValue( range ) )
        context.symbols.assign( "enumerate", CallablePythonValue( enumerate ) )
        context.symbols.assign( "len", CallablePythonValue( function_len ) )
        context.symbols.assign( "map", CallablePythonValue( map ) )
        context.symbols.assign( "filter", CallablePythonValue( filter ) )

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
        context.symbols.assign( "sfload", CallablePythonValue( function_sfload ) )
        context.symbols.assign( "sfunload", CallablePythonValue( function_sfunload ) )
        context.symbols.assign( "interval", Interval )
        context.symbols.assign( "scale", Scale )

        context.symbols.assign( "sequencers\\ABC", CallablePythonValue( seqs.ABCSequencer ) )
        context.symbols.assign( "sequencers\\PDF", CallablePythonValue( seqs.PDFSequencer ) )
        context.symbols.assign( "sequencers\\HTML", CallablePythonValue( seqs.HTMLSequencer ) )
        context.symbols.assign( "sequencers\\Midi", CallablePythonValue( seqs.MidiSequencer ) )
        context.symbols.assign( "sequencers\\Debug", CallablePythonValue( seqs.DebugSequencer ) )
        context.symbols.assign( "sequencers\\FluidSynth", CallablePythonValue( seqs.FluidSynthSequencer ) )

        context.symbols.assign( "Music", CallablePythonValue( Music ) )
        context.symbols.assign( "Metronome", CallablePythonValue( Metronome ) )
        context.symbols.assign( "met", CallablePythonValue( Metronome ) )

        context.symbols.assign( "voices\\create", CallablePythonValue( function_voices_create ) )

        # TODO: Make tests expose a script object
        if context.script is not None:
            context.script.import_module( self.context, Path( __file__ ).parent / "std.mkl", save_cache = False )
