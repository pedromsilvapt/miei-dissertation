from typing import List, Any
from core import Context, Music, Voice
from core.events import MusicEvent, NoteOnEvent, NoteOffEvent, ControlChangeEvent, ProgramChangeEvent
from core.theory import Note
import mido

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

def midi_stream_to_music ( stream : Any, voice : Voice ) -> Music:
    pass

def function_readmidi ( context : Context, file : str, voices : List[Voice] = None, ignore_types : List[str] = None ):
    mid = mido.MidiFile( file )
    
    events : List[MusicEvent] = []

    event = None

    # TODO Read tempo from midi file
    tempo = 416666

    for i, track in enumerate( mid.tracks ):
        if voices is None:
            msgVoice = context.voice
        else:
            msgVoice = voices[ i ]

        if msgVoice == None:
            continue

        ticks = 0

        for msg in list( track ):
            ticks += msg.time

            if ignore_types is not None and msg.type in ignore_types:
                continue

            time = context.cursor + int( mido.tick2second( ticks, mid.ticks_per_beat, tempo ) * 1000 )

            event = midi_to_event( time, msg, msgVoice )

            if event:
                events.append( event )
            else:
                pass
                # print( msg )

    return Music( events )
