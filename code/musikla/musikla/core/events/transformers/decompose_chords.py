from .transformer import Transformer
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from ..chord import ChordEvent, ChordOnEvent, ChordOffEvent
from collections import defaultdict
from typing import Callable

class DecomposeChordsTransformer( Transformer ):
    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if isinstance( event, ChordEvent ) or isinstance( event, ChordOnEvent ) or isinstance( event, ChordOffEvent ):
                for note in event.notes:
                    self.add_output( note )
            else:
                self.add_output( event )