from core import Context, Library
from core.callable_python_value import CallablePythonValue
from core import Value, Music
from core.events import NoteEvent
from core.theory import NotePitchClassesInv, NotePitchClassesIndexes
from parser.abstract_syntax_tree.expressions import VariableExpressionNode

def function_arpeggio_gen ( context : Context, chord : Music, pattern : Music = None, bars : int = None ):
    if pattern == None:
        baseline : int = None
        
        for event in chord:
            if baseline == None:
                baseline = event.end_timestamp
            else:
                event = event.clone( timestamp = baseline )

            context.cursor = event.end_timestamp

            yield event
    else:
        notes_pool = [ evt for evt in chord if isinstance( evt, NoteEvent ) ]

        for event in pattern:
            if not isinstance( event, NoteEvent ):
                yield event
                continue

            index = NotePitchClassesIndexes[ NotePitchClassesInv[ event.pitch_class ] ]

            archtype = notes_pool[ index ]

            event = archtype.from_pattern( event )

            context.cursor = event.end_timestamp

            yield event

def function_arpeggio ( context : Context, chord : Music, pattern : Music = None, bars : int = None ) -> Music:
    return Music( function_arpeggio_gen( context, chord, pattern, bars ) )

class MusicLibrary(Library):
    def on_link ( self ):
        context : Context = self.context

        context.symbols.assign( "arpeggio", CallablePythonValue( function_arpeggio ) )

