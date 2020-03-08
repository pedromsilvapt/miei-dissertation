from .transformer import Transformer
from ..event import MusicEvent
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from ..chord import ChordEvent
from ...music import MusicBuffer
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

class ComposeChordsTransformer( Transformer ):
    def __init__ ( self ):
        super().__init__()
        
        self.buffer : List[NoteEvent] = []
        self.last_timestamp : int = 0

    def flush_buffer ( self ):
        if not self.buffer:
            return
        
        if len( self.buffer ) == 1:
            self.add_output( self.buffer[ 0 ] )
        else:
            # We know that the first event in the buffer must be a note event
            # because we only append to the buffer if the event is a note event
            # or if the buffer already has any events in it
            first_name = self.buffer[ 0 ].voice.name
            
            # A variable that is true if all the note events in the buffer belong
            # to the same voice
            single_voice = all( ( ev.voice.name == first_name for ev in self.buffer if isinstance( ev, NoteEvent ) ) )

            per_voice : Dict[str, List[NoteEvent]] = {}

            voiceless : List[MusicEvent] = []

            for ev in self.buffer:
                if isinstance( ev, NoteEvent ):
                    voice_name = ev.voice.name

                    if voice_name not in per_voice:
                        per_voice[ voice_name ] = [ ev ]
                    else:
                        per_voice[ voice_name ].append( ev )
                else:
                    voiceless.append( ev )
            
            # TODO Handle notes played at the same time for the same voice
            # but with different durations
            for notes in per_voice.values():
                if len( notes ) <= 2:
                    for note in notes:
                        self.add_output( note )
                else:
                    self.add_output( ChordEvent(
                        timestamp = notes[ 0 ].timestamp,
                        pitches = [ int( n ) for n in notes ],
                        duration = max( ( n.duration for n in notes ) ),
                        value = max( ( n.value for n in notes ) ),
                        voice = notes[ 0 ].voice,
                        tied = notes[ 0 ].tied,
                        velocity = notes[ 0 ].velocity
                    ) )

            for ev in voiceless:
                self.add_output( ev )

        self.buffer.clear()

    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if event.timestamp != self.last_timestamp:
                self.flush_buffer()
            
            if isinstance( event, NoteEvent ) or self.buffer:
                self.buffer.append( event )
            else:
                self.add_output( event ) 
            
            self.last_timestamp = event.timestamp

        self.flush_buffer()