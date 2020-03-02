from .transformer import Transformer
from ..event import MusicEvent
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from ...music import MusicBuffer
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

class ComposeNotesTransformer( Transformer ):
    def transform ( self ):
        on_events : Dict[Tuple[str, int], NoteOnEvent] = {}

        # Caches what is the earliest note_on we have received that is still waiting for the matching corresponding note_off
        # This allows us to quickly check if we can flush some of the events of the buffer
        # Without having to check every buffered on_events
        # Next Event Timestamp
        net = None
        # Next Event Count
        nec = 0

        buffered_events : MusicBuffer = MusicBuffer()

        while True:
            done, event = yield

            if done: break

            if isinstance( event, NoteOffEvent ):
                key = ( event.voice.name, int( event ) )

                if key in on_events:
                    on_event = on_events[ key ]

                    duration = event.timestamp - on_event.timestamp
                    value = on_event.voice.from_duration_absolute( duration )

                    del on_events[ key ]

                    composed_event = NoteEvent(
                        timestamp = on_event.timestamp,
                        pitch_class = on_event.pitch_class,
                        value = value,
                        duration = duration,
                        octave = on_event.octave,
                        voice = on_event.voice,
                        velocity = on_event.velocity,
                        accidental = on_event.accidental
                    )

                    buffered_events.append( composed_event )

                    # If the next event timestamp is the same as the one we just composed
                    # We need to update it and possibly flush the buffer
                    if net == composed_event.timestamp:
                        if nec > 1:
                            nec -= 1
                        else:
                            net = None
                            nec = 0

                            for event in on_events.values():
                                if nec == 0 or net > event.timestamp:
                                    net, nec = ( event.timestamp, 1 )
                                elif net == event.timestamp:
                                    nec = nec + 1

                            for flushed_event in buffered_events.collect( None if nec == 0 else net ):
                                self.add_output( flushed_event )
            elif isinstance( event, NoteOnEvent ):
                on_events[ ( event.voice.name, int( event ) ) ] = event

                if nec == 0 or net > event.timestamp:
                    net, nec = ( event.timestamp, 1 )
                elif net == event.timestamp:
                    nec = nec + 1
            elif buffered_events:
                buffered_events.append( event )
            else:
                self.add_output( event )

        for event in buffered_events.collect():
            self.add_output( event )