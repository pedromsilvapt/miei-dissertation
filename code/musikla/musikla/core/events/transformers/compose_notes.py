from .transformer import Transformer
from ..event import MusicEvent
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

def split ( it, predicate ):
    a = []
    b = []

    for item in it:
        if predicate( item ):
            a.append( item )
        else:
            b.append( item )

    return a, b

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

        buffered_events : List[MusicEvent] = []

        while True:
            done, event = yield

            if done: break

            if isinstance( event, NoteOffEvent ):
                key = ( event.voice.name, int( event ) )

                if key in on_events:
                    on_event = on_events[ key ]

                    # TODO Calculate propert duration
                    duration = on_event.voice.get_value( event.timestamp - on_event.timestamp )

                    composed_event = NoteEvent(
                        timestamp = on_event.timestamp,
                        pitch_class = on_event.pitch_class,
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

                            flushed, buffered_events = split( buffered_events, lambda ev: nec == 0 or ev.timestamp <= net )

                            for flushed_event in flushed:
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

        for event in sorted( buffered_events, key = lambda ev: ev.timestamp ):
            self.add_output( event )