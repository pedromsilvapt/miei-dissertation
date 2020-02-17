from .transformer import Transformer
from ..event import MusicEvent
from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from collections import defaultdict
from typing import Callable, Dict, List, Tuple

class BalanceNotesTransformer( Transformer ):
    def __init__ ( self, get_time : Callable ):
        super().__init__()

        self.get_time : Callable = get_time

    def transform ( self ):
        tracker = NoteTracker()

        while True:
            done, value = yield

            if done: break

            tracker.process( value )

            self.add_output( value )

        for event in tracker.close( self.get_time() ):
            self.add_output( event )

class NoteTracker:
    def __init__ ( self ):
        self.active_notes = []

    def activate ( self, note_on : NoteOnEvent ):
        self.active_notes.append( note_on )

    def deactivate ( self, note_off : NoteOffEvent ):
        match_index = None

        for i, on in enumerate( self.active_notes ):
            if on.voice.name == note_off.voice.name and int( on ) == int( note_off ):
                match_index = i

        if match_index != None:
            del self.active_notes[ match_index ]

    def process ( self, event ):
        if isinstance( event, NoteOnEvent ):
            self.activate( event )
        elif isinstance( event, NoteOffEvent ):
            self.deactivate( event )

    def close ( self, time : int ):
        for on in self.active_notes:
            yield on.note_off( time )
