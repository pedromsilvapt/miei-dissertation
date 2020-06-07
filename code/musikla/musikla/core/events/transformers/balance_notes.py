from typing import Optional
from .transformer import Transformer
from ..note import NoteOnEvent, NoteOffEvent
from ..chord import ChordOnEvent, ChordOffEvent
from typing import Callable, List, Tuple

class BalanceNotesTransformer( Transformer ):
    def __init__ ( self, get_time : Callable = None ):
        super().__init__()

        self.get_time : Optional[Callable] = get_time

    def transform ( self ):
        tracker = NoteTracker()

        last_time : int = 0

        while True:
            done, value = yield

            if done: break

            last_time = max( value.end_timestamp, last_time )

            tracker.process( value )

            self.add_output( value )

        for event in tracker.close( last_time if self.get_time is None else self.get_time() ):
            self.add_output( event )

class NoteTracker:
    def __init__ ( self ):
        self.active_notes : List[NoteOnEvent] = []
        self.active_chords : List[ChordOnEvent] = []

    def activate ( self, note_on : NoteOnEvent ):
        self.active_notes.append( note_on )

    def deactivate ( self, note_off : NoteOffEvent ):
        match_index = None

        for i, on in enumerate( self.active_notes ):
            if on.voice.name == note_off.voice.name and int( on ) == int( note_off ):
                match_index = i

        if match_index != None:
            del self.active_notes[ match_index ]

    def activate_chord ( self, chord_on : ChordOnEvent ):
        self.active_chords.append( chord_on )

    def deactivate_chord ( self, chord_off : ChordOffEvent ):
        match_index = None

        for i, on in enumerate( self.active_chords ):
            if on.voice.name == chord_off.voice.name and on.pitches == chord_off.pitches:
                match_index = i

        if match_index != None:
            del self.active_chords[ match_index ]

    def process ( self, event ):
        if isinstance( event, NoteOnEvent ):
            self.activate( event )
        elif isinstance( event, NoteOffEvent ):
            self.deactivate( event )
        elif isinstance( event, ChordOnEvent ):
            self.activate_chord( event )
        elif isinstance( event, ChordOffEvent ):
            self.deactivate_chord( event )

    def close ( self, time : int ):
        for on in self.active_notes:
            yield on.note_off( time )
        
        for on in self.active_chords:
            yield on.chord_off( time )
