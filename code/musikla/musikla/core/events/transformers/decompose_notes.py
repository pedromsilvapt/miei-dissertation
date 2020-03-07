from .transformer import Transformer
from musikla.core import MusicBuffer
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from ..chord import ChordEvent, ChordOnEvent, ChordOffEvent
from collections import defaultdict
from typing import Callable

class DecomposeNotesTransformer( Transformer ):
    def transform ( self ):
        offs : MusicBuffer = MusicBuffer()

        while True:
            done, event = yield

            if done: break

            for ev in offs.collect( event.timestamp ):
                self.add_output( ev )
            
            if isinstance( event, NoteEvent ):
                offs.append( event.note_off )

                self.add_output( event.note_on )
            elif isinstance( event, ChordEvent ):
                offs.append( event.chord_off )

                self.add_output( event.chord_on )
            else:
                self.add_output( event )

        for event in offs.collect():
            self.add_output( event )