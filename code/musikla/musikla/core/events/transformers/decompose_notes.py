from .transformer import Transformer
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from collections import defaultdict
from typing import Callable

class DecomposeNotesTransformer( Transformer ):
    def transform ( self ):
        offs = []

        next_off = None

        while True:
            done, event = yield

            if done: break

            while offs and next_off <= event.timestamp:
                for ev in offs: 
                    if ev.timestamp <= next_off:
                        self.add_output( ev )

                offs = [ ev for ev in offs if ev.timestamp > next_off ]

                next_off = min( ev.timestamp for ev in offs ) if offs else None

            if isinstance( event, NoteEvent ):
                event_off = event.note_off

                offs.append( event_off )

                if next_off == None or next_off > event_off.timestamp:
                    next_off = event_off.timestamp

                self.add_output( event.note_on )
            else:
                self.add_output( event )

        for event in sorted( offs, key = lambda ev: ev.timestamp ):
            self.add_output( event )