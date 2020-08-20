from typing import Tuple, List, Dict, Optional, Union
from musikla.core import Context, Library
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core import Music
from musikla.core.events import NoteEvent, SoundEvent, ChordEvent
from musikla.core.events.transformers import Transformer, VoiceIdentifierTransformer, NotationBuilderTransformer, DecomposeChordsTransformer
from musikla.parser.abstract_syntax_tree import Node
from musikla.parser.abstract_syntax_tree.music_parallel_node import Box
from musikla.parser.abstract_syntax_tree.macros import VoiceDeclarationMacroNode

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
    def __init__ ( self, 
        only_final : bool = False, 
        ast : bool = False, 
        context : Context = None, 
        nameless_voices : bool = True, 
        declare_voices : bool = True, 
        base_voice : Voice = None 
    ):
        """
        only_final          When true, the result is only emitted after the entire 
                            input (musical sequence) has been processed. When false,
                            intermediate notations are continuously emitted.
        
        ast                 When true, emits the Abstract Syntax Tree objects. When
                            false, transforms those objects into a string that can
                            be parsed, and emits the string instead

        nameless_voices     When true, it tries to produce notation that carries with
                            it any state that is needed, instead of prepending 
                            the names of the voices the events belonged to
        
        declare_voices      When `nameless_voices = False`, also include the 
                            definitions of the named voices used.
        
        base_voice          ...
        """
        super().__init__( only_final )

        self.ast : bool = ast
        self.context : Context = context or Context.create()
        self.nameless_voices : bool = nameless_voices
        self.declare_voices : bool = declare_voices
        self.base_voice : Voice = base_voice or Voice()

    def _get_voice_name ( self, voice : Voice ) -> str:
        return voice.name.split( "/" )[ 0 ]


    def note_to_ast ( self, context : Context, voice : Voice, event : NoteEvent ) -> ast.NoteNode:
        return ast.NoteNode( Note(
            pitch_class = event.pitch_class,
            octave = event.octave - voice.octave,
            accidental = event.accidental,
            value = voice.get_relative_value( event.value )
        ) )

    def event_to_ast ( self, context : Context, voice : Voice, events : List[ast.Node], event : MusicEvent ):
        if not any( isinstance( event, eventType ) for eventType in [ evt.NoteEvent, evt.ChordEvent, evt.RestEvent ] ):
            return

        if isinstance( event, evt.NoteEvent ) and event.velocity != voice.velocity:
            voice = voice.clone( velocity = event.velocity )

            events.append( ast_mod.VelocityModifierNode( event.velocity ) )
        
        if isinstance( event, evt.NoteEvent ):
            events.append( self.note_to_ast( context, voice, event ) )
        elif isinstance( event, evt.ChordEvent ):
            events.append( ast.ChordNode( Chord(
                notes = [ self.note_to_ast( context, voice, n ).note for n in event.notes ],
                name = event.name,
                value = voice.get_relative_value( event.value )
            ) ) )
        elif isinstance( event, evt.RestEvent ):
            events.append( ast.RestNode(
                value = voice.get_relative_value( event.value ),
                visible = event.visible
            ) )

    def event_sequence_to_ast ( self, context : Context, voice: Voice, events : List[MusicEvent] ) -> ast.MusicSequenceNode:
        nodes : List[ast.Node] = []

        for ev in events:
            self.event_to_ast( context, voice, nodes, ev )

        return ast.MusicSequenceNode( nodes )

    def modifiers_to_ast ( self, base_voice : Voice, actual_voice : Voice, music : ast.MusicSequenceNode = None ) -> Optional[ast.MusicSequenceNode]:
        """
        Compares the settings between `base_voice` and `actual_voice`. When a
        difference is found, creates a AST node describing the value on 
        `actual_voice`.
        """
        mods : List[ast_mod.ContextModifierNode] = []

        if base_voice.time_signature != actual_voice.time_signature: # (4, 4):
            u, d = actual_voice.time_signature
            mods.append( ast_mod.SignatureModifierNode( u, d ) )

        if base_voice.tempo != actual_voice.tempo: # 60:
            mods.append( ast_mod.TempoModifierNode( actual_voice.tempo ) )

        if base_voice.octave != actual_voice.octave: # 4:
            mods.append( ast_mod.OctaveModifierNode( actual_voice.octave ) )

        if base_voice.value != actual_voice.value: # 1:
            mods.append( ast_mod.LengthModifierNode( actual_voice.value ) )

        if base_voice.velocity != actual_voice.velocity: # 127:
            mods.append( ast_mod.VelocityModifierNode( actual_voice.velocity ) )

        if mods and music:
            mods.extend( music.expressions )

            return ast.MusicSequenceNode( mods )
        elif mods:
            return ast.MusicSequenceNode( mods )
        else:
            return music or None

    def voice_to_ast ( self, context: Context, voice : Voice, music : ast.MusicSequenceNode = None, base_voice : Voice = None ) -> Union[ast_mod.VoiceBlockModifier, ast.MusicSequenceNode, None]:
        if self.nameless_voices:
            return self.modifiers_to_ast( base_voice or self.base_voice, voice, music = music )
        else:
            name = self._get_voice_name( voice )
            
            music = self.modifiers_to_ast( base_voice or voice, voice, music = music )

            if name == context.voice.name:
                return music
            else:
                return ast_mod.VoiceBlockModifier( music, name )
        
    def voice_sequence_to_ast ( self, context : Context, voice : Tuple[Voice, int, List[MusicEvent]], base_voice : Voice = None ) -> Union[ast_mod.VoiceBlockModifier, ast.MusicSequenceNode, None]:
        sequence = self.event_sequence_to_ast( context, voice[ 0 ], voice[ 2 ] )

        if not sequence.expressions:
            return None
        
        return self.voice_to_ast( context, voice[ 0 ], sequence, base_voice = base_voice )

    def voice_declaration_to_ast ( self, base_voice : Voice, actual_voice : Voice ) -> VoiceDeclarationMacroNode:
        name = self._get_voice_name( actual_voice )

        return VoiceDeclarationMacroNode(
            name = name,
            modifiers = self.modifiers_to_ast( base_voice, actual_voice ) or ast_exp.MusicSequenceNode()
        )

    def to_ast ( self, events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] ) -> ast.Node:
        l = len( events_per_voice )

        if l == 0:
            return ast.MusicSequenceNode( [] )
        elif l == 1:
            staff = self.voice_sequence_to_ast( self.context.fork(), events_per_voice[ 0 ] )

            # When there are no notes on this staff, there's also no need to even
            # generate the voice declarations. We just return an empty group ()
            if staff is None:
                return ast_exp.GroupNode()
            
            # decl will contain the voice declaration used for this staff, if
            # voice declarations are enabled
            decl : Optional[VoiceDeclarationMacroNode] = None

            if not self.nameless_voices and self.declare_voices:
                decl = self.voice_declaration_to_ast( self.base_voice, events_per_voice[ 0 ][ 0 ] )
    
                return ast_stm.StatementsListNode( [ decl, staff ] )

            return staff
        else:
            decls : List[VoiceDeclarationMacroNode] = []
            # Sometimes voices can have the same name but slightly different
            # settings. When that happens, we want to keep a reference to what
            # version of that voice we created a declaration for. That way we can
            # generate any extras modifiers needed to apply those changes
            decls_voices : Dict[str, Voice] = {}

            staffs : List[ast.Node] = []

            for voice_staff in events_per_voice:
                voice, _, _ = voice_staff
                
                name = self._get_voice_name( voice )

                base_voice = self.base_voice

                if not self.nameless_voices and self.declare_voices:
                    if name not in decls_voices:
                        decls.append( self.voice_declaration_to_ast( self.base_voice, voice ) )

                        decls_voices[ name ] = voice

                        base_voice = voice

                staff_expr = self.voice_sequence_to_ast( self.context.fork(), voice_staff, base_voice = base_voice )

                if staff_expr is not None:
                    staffs.append( staff_expr )

            if not staffs:
                return ast_exp.GroupNode()

            music_expr = ast.MusicParallelNode( staffs )

            if not decls:
                return music_expr
            
            return ast_stm.StatementsListNode( [
                *decls,
                music_expr
            ] )

    def to_string ( self, events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] ) -> Union[str, ast.Node]:
        if self.ast:
            return self.to_ast( events_per_voice )
        else:
            ast = self.to_ast( events_per_voice )

            printer = CodePrinter()

            return printer.print( ast )

def function_sample ( context : Context, file : str, duration : float = None, len = None ):
    event = SoundEvent( file, timestamp = context.cursor, voice = context.voice, duration = duration, value = len, velocity = context.voice.velocity )

    context.cursor += event.duration

    return Music( [ event ] )

def function_transpose ( note, semitones : int = 0, octaves : int = 1 ):
    if isinstance( note, NoteEvent ):
        note = note.clone(
            octave = note.octave + octaves
        )
    
    return note

def function_to_mkl ( context : Context, music : Music, 
        ast : bool = False, 
        nameless_voices: bool = True, 
        declare_voices : bool = True, 
        base_voice : Voice = None  ) -> Union[str, Node]:
    source : Box[str] = Box( "" )

    inp, out = Transformer.pipeline2(
        VoiceIdentifierTransformer(), 
        MusiklaNotationBuilderTransformer( 
            only_final = True, 
            ast = ast, 
            context = context, 
            nameless_voices = nameless_voices,
            declare_voices = declare_voices,
            base_voice = base_voice
        ),
    )

    out.subscribe( lambda s: source.set( s ) )

    for ev in music.expand( context.fork( cursor = 0 ) ):
        inp.add_input( ev )
    
    inp.end_input()

    return source.value

def function_chord ( context : Context, *notes ):
    notes = [ n.first_note() if isinstance( n, Music ) else n for n in notes ]

    chord = ChordEvent(
        timestamp = context.cursor, 
        pitches = [ int(n) for n in notes  ], 
        name = None, 
        duration = notes[ 0 ].duration, 
        voice = notes[ 0 ].voice, 
        velocity = notes[ 0 ].velocity, 
        value = notes[ 0 ].value, 
        tied = notes[ 0 ].tied, 
        staff = notes[ 0 ].staff
    )

    return Music( [ chord ] )

class MusicLibrary(Library):
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( 'chord', CallablePythonValue( function_chord ) );

        context.symbols.assign( 'is_sample_optimized', CallablePythonValue( SoundEvent.is_optimized ) )
        context.symbols.assign( 'optimize_sample', CallablePythonValue( SoundEvent.optimize ) )
        context.symbols.assign( 'optimize_samples_folder', CallablePythonValue( SoundEvent.optimize_folder ) )
        context.symbols.assign( "sample", CallablePythonValue( function_sample ) )

        context.symbols.assign( "transpose", CallablePythonValue( function_transpose ) )
        context.symbols.assign( "to_mkl", CallablePythonValue( function_to_mkl ) )


