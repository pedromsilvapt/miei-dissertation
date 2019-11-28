from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from typing import List

def decompose_notes ( notes ):
    offs = []

    next_off = None

    for event in notes:
        while offs and next_off <= event.timestamp:
            for ev in offs: 
                if ev.timestamp <= next_off:
                    yield ev

            offs = [ ev for ev in offs if ev.timestamp > next_off ]

            next_off = min( ev.timestamp for ev in offs )

        if isinstance( event, NoteEvent ):
            event_off = event.note_off

            offs.append( event_off )

            if next_off == None or next_off > event_off.timestamp:
                next_off = event_off.timestamp

            yield event.note_on
        else:
            yield event

    for event in sorted( offs, key = lambda ev: ev.timestamp ):
        yield event

