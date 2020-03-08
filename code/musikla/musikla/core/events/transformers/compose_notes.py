from .transformer import Transformer
from ..event import MusicEvent
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from ..chord import ChordEvent, ChordOnEvent, ChordOffEvent
from ...music import MusicBuffer
from collections import defaultdict
from typing import Callable, Dict, List, Tuple, Any, Union, Optional

class ComposeNotesTransformer( Transformer ):
    def __init__ ( self ):
        super().__init__()
        
        self.on_events : Dict[Any, Union[NoteOnEvent, ChordOnEvent]] = {}
        self.buffered_events : MusicBuffer = MusicBuffer()

        # Caches what is the earliest note_on we have received that is still waiting for the matching corresponding note_off
        # This allows us to quickly check if we can flush some of the events of the buffer
        # Without having to check every buffered on_events
        # Next Event Timestamp
        self.net : Optional[int] = None
        # Next Event Count
        self.nec : int = 0

    def _get_note_key ( self, event : Union[NoteOnEvent, NoteOffEvent] ):
        return ( event.voice.name, int( event ) )

    def _off_event ( self, timestamp ):
        # If the next event timestamp is the same as the one we just composed
        # We need to update it and possibly flush the buffer
        if self.net == timestamp:
            if self.nec > 1:
                self.nec -= 1
            else:
                self.net = None
                self.nec = 0

                for event in self.on_events.values():
                    if self.nec == 0 or self.net > event.timestamp:
                        self.net, self.nec = ( event.timestamp, 1 )
                    elif self.net == event.timestamp:
                        self.nec = self.nec + 1

                for flushed_event in self.buffered_events.collect( None if self.nec == 0 else self.net ):
                    self.add_output( flushed_event )

    def _on_event ( self, timestamp : int ):
        if self.nec == 0 or self.net > timestamp:
            net, nec = ( timestamp, 1 )
        elif net == timestamp:
            nec = nec + 1

    def _on_note_off ( self, event : NoteOffEvent ):
        key = self._get_note_key( event )

        if key in self.on_events:
            on_event = self.on_events[ key ]

            duration = event.timestamp - on_event.timestamp
            value = on_event.voice.from_duration_absolute( duration )

            composed_event = NoteEvent(
                timestamp = on_event.timestamp,
                pitch_class = on_event.pitch_class,
                value = value,
                duration = duration,
                octave = on_event.octave,
                voice = on_event.voice,
                velocity = on_event.velocity,
                accidental = on_event.accidental,
                tied = on_event.tied
            )

            self.buffered_events.append( composed_event )

            del self.on_events[ key ]

            self._off_event( composed_event.timestamp )
    
    def _on_note_on ( self, event : NoteOnEvent ):
        self.on_events[ self._get_note_key( event ) ] = event

        self._on_event( event.timestamp )

    def _get_chord_key ( self, event : Union[ChordOnEvent, ChordOffEvent] ):
        return ( event.voice.name, tuple( event.pitches ) )

    def _on_chord_off ( self, event : ChordOffEvent ):
        key = self._get_chord_key( event )

        if key in self.on_events:
            on_event = self.on_events[ key ]

            duration = event.timestamp - on_event.timestamp
            value = on_event.voice.from_duration_absolute( duration )

            composed_event = ChordEvent(
                timestamp = on_event.timestamp,
                pitches = on_event.pitches,
                name = on_event.name,
                value = value,
                duration = duration,
                voice = on_event.voice,
                velocity = on_event.velocity,
                tied = on_event.tied
            )

            self.buffered_events.append( composed_event )

            del self.on_events[ key ]

            self._off_event( composed_event.timestamp )
    
    def _on_chord_on ( self, event : ChordOnEvent ):
        self.on_events[ self._get_chord_key( event ) ] = event

        self._on_event( event.timestamp )

    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if isinstance( event, NoteOffEvent ):
                self._on_note_off( event )
            elif isinstance( event, NoteOnEvent ):
                self._on_note_on( event )
            elif isinstance( event, ChordOffEvent ):
                self._on_chord_off( event )
            elif isinstance( event, ChordOnEvent ):
                self._on_chord_on( event )
            elif self.buffered_events:
                self.buffered_events.append( event )
            else:
                self.add_output( event )

        for event in self.buffered_events.collect():
            self.add_output( event )