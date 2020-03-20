from typing import Any, List, Optional
from musikla.core import Context, Library
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core import Value, Music
from musikla.core.events import NoteEvent, SoundEvent
from musikla.core.theory import NotePitchClassesInv, NotePitchClassesIndexes
from musikla.parser.abstract_syntax_tree.expressions import VariableExpressionNode

def function_arpeggio_gen ( context : Context, chord : Music, pattern : Music = None, bars : int = None ):
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

        for event in pattern:
            if not isinstance( event, NoteEvent ):
                yield event
                continue

            index = NotePitchClassesIndexes[ NotePitchClassesInv[ event.pitch_class ] ]

            archtype = notes_pool[ index ]

            event = archtype.from_pattern( event )

            context.cursor = event.end_timestamp

            yield event

def function_sample ( context : Context, file : str, duration : float = None, len = None ):
    event = SoundEvent( file, timestamp = context.cursor, voice = context.voice, duration = duration, value = len )

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

class MusicLibrary(Library):
    def on_link ( self ):
        context : Context = self.context

        context.symbols.assign( "sample", CallablePythonValue( function_sample ) )
        context.symbols.assign( "arpeggio", CallablePythonValue( function_arpeggio ) )
        context.symbols.assign( "transpose", CallablePythonValue( function_transpose ) )


