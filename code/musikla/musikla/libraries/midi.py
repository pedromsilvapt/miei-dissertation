from typing import List, Any, Union
from musikla.core import Context, Music, Voice, Library, Clock
from musikla.core.callable_python_value import CallablePythonValue
from musikla.core.events import MusicEvent, NoteOnEvent, NoteOffEvent, ControlChangeEvent, ProgramChangeEvent
from musikla.core.theory import Note
from musikla.core.events.transformers import ComposeNotesTransformer, TerminationMelodyTransformer, TeeTransformer, VoiceIdentifierTransformer, MusiklaNotationBuilderTransformer, Transformer
import mido
from mido.ports import MultiPort

def midi_to_event ( time : int, msg : Any, voice : Voice ):
    if msg.type == 'control_change':
        return ControlChangeEvent( time, voice, msg.control, msg.value )
    elif msg.type == 'program_change':
        pass
        # return ProgramChangeEvent( time, voice, msg.program )
    elif msg.type == 'note_on':
        note = Note().with_pitch( msg.note )

        return NoteOnEvent( 
            timestamp = time, 
            pitch_class = note.pitch_class, 
            octave = note.octave, 
            accidental = note.accidental, 
            velocity = msg.velocity, 
            voice = voice 
        )
    elif msg.type == 'note_off':
        note = Note().with_pitch( msg.note )

        return NoteOffEvent( 
            timestamp = time, 
            pitch_class = note.pitch_class, 
            octave = note.octave, 
            accidental = note.accidental,
            voice = voice 
        )
        
    return None

def midi_track_to_music ( 
        context, mid, stream : Any, voice : Voice, 
        ignore_message_types : List[str] = None 
    ):
    # TODO Read tempo from midi file
    tempo = 416666

    ticks = 0

    for msg in stream:
        ticks += msg.time

        if ignore_message_types is not None and msg.type in ignore_message_types:
            continue

        time = context.cursor + int( mido.tick2second( ticks, mid.ticks_per_beat, tempo ) * 1000 )

        event = midi_to_event( time, msg, voice )

        if event:
            yield event
        else:
            pass

def midi_stream_to_music ( 
        context, stream : Any, voice : Voice, 
        ignore_message_types : List[str] = None 
    ):
    clock = Clock()

    start = context.cursor

    for msg in stream:
        if ignore_message_types is not None and msg.type in ignore_message_types:
            continue

        time = start + clock.elapsed()

        event = midi_to_event( time, msg, voice )

        if event:
            yield event
        else:
            pass

def read_midi_file (
        context : Context, 
        file : mido.MidiFile = None,
        voices : List[Voice] = None,
        cutoff_sequence = None,
        ignore_message_types : List[str] = None
    ):
    tracks = []

    for i, track in enumerate( file.tracks ):
        if voices is None:
            msgVoice = context.voice
        else:
            msgVoice = voices[ i ]

        if msgVoice == None:
            continue

        events = midi_track_to_music( context, file, track, msgVoice, ignore_message_types )
            
        events = ComposeNotesTransformer.iter( events )

        tracks.append( events )

    return Music.parallel( tracks )

def function_readmidi (
        context : Context, 
        file : str = None, 
        port : Union[str, List[str], bool] = None, 
        voices : List[Voice] = None,
        cutoff_sequence = None,
        ignore_message_types : List[str] = None
    ):
    if file is not None:
        mid = mido.MidiFile( file )

        return read_midi_file( context, mid, voices, cutoff_sequence, ignore_message_types )
    else:
        if port == True:
            default_port = context.library( MidiLibrary ).get_midi_default_input()

            if default_port is None:
                port = mido.open_input()
            else:
                port = mido.open_input( default_port )
        elif type(port) == str:
            port = mido.open_input( port )
        elif type(port) == list:
            port = MultiPort( [ mido.open_input( p ) for p in port ] )
        
        events = midi_stream_to_music( context, port, context.voice, ignore_message_types )

        events = ComposeNotesTransformer.iter( events )

        if cutoff_sequence != None:
            events = TerminationMelodyTransformer.iter( events, list( cutoff_sequence.expand( context.fork( cursor = 0 ) ) ) )

        events = TeeTransformer.iter( 
            events, 
            Transformer.pipeline(
                VoiceIdentifierTransformer(),
                MusiklaNotationBuilderTransformer(),
                Transformer.subscriber( lambda n: print( n + '\n\n' ) )
            )
        )

        return Music( list( events ) )

def function_get_midi_input_name ( context : Context ) -> str:
    return context.library( MidiLibrary ).get_midi_default_input()

def function_set_midi_input_name ( context : Context, name : str ):
    context.library( MidiLibrary ).set_midi_default_input( name )

class MidiLibrary(Library):
    def on_link ( self, script ):
        context : Context = self.context

        context.symbols.assign( "readmidi", CallablePythonValue( function_readmidi ) )
        context.symbols.assign( "get_midi_input_name", CallablePythonValue( function_get_midi_input_name ) )
        context.symbols.assign( "set_midi_input_name", CallablePythonValue( function_set_midi_input_name ) )

    def set_midi_default_input ( self, name : str ):
        self.context.symbols.assign( "midi_default_input", name, container = "internal" )

    def get_midi_default_input ( self ) -> str:
        return self.context.symbols.lookup( "midi_default_input", container = "internal" )