from typing import Any, List, Optional, Union

from typing import Tuple
from musikla.core import Context, Library
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core import Music
from musikla.core.events import NoteEvent, SoundEvent
from musikla.core.theory import NotePitchClassesInv, NotePitchClassesIndexes
from musikla.core.events.transformers import Transformer, AnnotateTransformer, VoiceIdentifierTransformer, NotationBuilderTransformer, DecomposeChordsTransformer
from musikla.parser.abstract_syntax_tree import Node
from musikla.parser.abstract_syntax_tree.music_parallel_node import Box

## NotationBuilder ##
from musikla.core.voice import Voice
from musikla.core.events.event import MusicEvent
from musikla.core.theory import Note, Chord
from musikla.parser.printer import CodePrinter
import musikla.core.events as evt
import musikla.parser.abstract_syntax_tree as ast
import musikla.parser.abstract_syntax_tree.expressions as ast_exp
import musikla.parser.abstract_syntax_tree.statements as ast_stm
import musikla.parser.abstract_syntax_tree.context_modifiers as ast_mod

class MusiklaNotationBuilderTransformer(NotationBuilderTransformer):
    def __init__ ( self, only_final : bool = False, ast : bool = False, context : Context = None ):
        super().__init__(  only_final )

        self.ast : bool = ast
        self.context : Context = context or Context.create()

    # def voice_to_string ( self, voice : Tuple[Voice, int, List[MusicEvent]] ) -> str:
    #     return f":{voice[ 0 ].name} " + ' '.join( map( str, voice[ 2 ] ) )
    
    def note_to_ast ( self, context : Context, event : NoteEvent ) -> ast.NoteNode:
        return ast.NoteNode( Note(
            pitch_class = event.pitch_class,
            octave = event.octave - context.voice.octave,
            accidental = event.accidental,
            value = context.voice.get_relative_value( event.value )
        ) )

    def event_to_ast ( self, context : Context, events : List[ast.Node], event : MusicEvent ):
        if not any( isinstance( event, eventType ) for eventType in [ evt.NoteEvent, evt.ChordEvent, evt.RestEvent ] ):
            return

        if isinstance( event, evt.NoteEvent ) and event.velocity != context.voice.velocity:
            context.voice = context.voice.clone( velocity = event.velocity )

            events.append( ast_mod.VelocityModifierNode( event.velocity ) )
        
        if isinstance( event, evt.NoteEvent ):
            events.append( self.note_to_ast( context, event ) )
        elif isinstance( event, evt.ChordEvent ):
            events.append( ast.ChordNode( Chord(
                notes = [ self.note_to_ast( context, n ).note for n in event.notes ],
                name = event.name,
                value = context.voice.get_relative_value( event.value )
            ) ) )
        elif isinstance( event, evt.RestEvent ):
            events.append( ast.RestNode(
                value = context.voice.get_relative_value( event.value ),
                visible = event.visible
            ) )

    def event_sequence_to_ast ( self, context : Context, events : List[MusicEvent] ) -> ast.MusicSequenceNode:
        nodes : List[ast.Node] = []

        for ev in events:
            self.event_to_ast( context, nodes, ev )

        return ast.MusicSequenceNode( nodes )

    def voice_to_ast ( self, context : Context, voice : Tuple[Voice, int, List[MusicEvent]] ) -> ast_mod.VoiceBlockModifier:
        return ast_mod.VoiceBlockModifier( self.event_sequence_to_ast( context, voice[ 2 ] ), voice[ 0 ].name )

    def to_ast ( self, events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] ) -> ast.Node:
        l = len( events_per_voice )

        if l == 0:
            return ast.MusicSequenceNode( [] )
        elif l == 1:
            return self.voice_to_ast( self.context.fork(), events_per_voice[ 0 ] )
        else:
            return ast.MusicParallelNode( [ self.voice_to_ast( self.context.fork(), v ) for v in events_per_voice ] )

    def to_string ( self, events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] ) -> Union[str, ast.Node]:
        if self.ast:
            return self.to_ast( events_per_voice )
        else:
            ast = self.to_ast( events_per_voice )

            printer = CodePrinter()

            return printer.print( ast )

def function_arpeggio_gen ( context : Context, chord : Music, pattern : Music = None, bars : int = None ):
    chord = chord.transform( DecomposeChordsTransformer )

    if pattern == None:
        baseline : Optional[int] = None
        
        for event in chord:
            if baseline == None:
                baseline = event.end_timestamp
            else:
                event = event.clone( timestamp = baseline )

            context.cursor = event.end_timestamp

            yield event
    else:
        notes_pool : List[Any] = [ evt for evt in chord if isinstance( evt, NoteEvent ) ]
        
        for event in pattern.transform( DecomposeChordsTransformer ):
            if not isinstance( event, NoteEvent ):
                yield event
                continue

            index = NotePitchClassesIndexes[ NotePitchClassesInv[ event.pitch_class ] ]

            archtype = notes_pool[ index ]

            event = archtype.from_pattern( event )
            
            context.cursor = event.end_timestamp

            yield event

def function_sample ( context : Context, file : str, duration : float = None, len = None ):
    event = SoundEvent( file, timestamp = context.cursor, voice = context.voice, duration = duration, value = len, velocity = context.voice.velocity )

    context.cursor += event.duration

    return Music( [ event ] )

def function_arpeggio ( context : Context, chord : Music, pattern : Music = None, bars : int = None ) -> Music:
    return Music( function_arpeggio_gen( context, chord, pattern, bars ) )

def function_transpose ( note, semitones : int = 0, octaves : int = 1 ):
    if isinstance( note, NoteEvent ):
        note = note.clone(
            octave = note.octave + octaves
        )
    
    return note

def function_to_mkl ( context : Context, music : Music, ast : bool = False ) -> Union[str, Node]:
    source : Box[str] = Box( "" )

    inp, out = Transformer.pipeline2(
        AnnotateTransformer(), 
        VoiceIdentifierTransformer(), 
        MusiklaNotationBuilderTransformer( only_final = True, ast = ast, context = context ),
    )

    out.subscribe( lambda s: source.set( s ) )

    for ev in music.expand( context.fork( cursor = 0 ) ):
        inp.add_input( ev )
    
    inp.end_input()

    return source.value

class MusicLibrary(Library):
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( 'is_sample_optimized', CallablePythonValue( SoundEvent.is_optimized ) )
        context.symbols.assign( 'optimize_sample', CallablePythonValue( SoundEvent.optimize ) )
        context.symbols.assign( 'optimize_samples_folder', CallablePythonValue( SoundEvent.optimize_folder ) )
        context.symbols.assign( "sample", CallablePythonValue( function_sample ) )

        context.symbols.assign( "arpeggio", CallablePythonValue( function_arpeggio ) )
        context.symbols.assign( "transpose", CallablePythonValue( function_transpose ) )
        context.symbols.assign( "to_mkl", CallablePythonValue( function_to_mkl ) )


