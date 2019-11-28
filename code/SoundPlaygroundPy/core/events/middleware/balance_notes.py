from ..note import NoteEvent, NoteOnEvent, NoteOffEvent
from collections import defaultdict
from typing import Callable

class NoteTracker:
    def __init__ ( self ):
        self.active_notes = []

    def activate ( self, note_on : NoteOnEvent ):
        self.active_notes.append( note_on )

    def deactivate ( self, note_off : NoteOffEvent ):
        match_index = None

        for i, on in enumerate( self.active_notes ):
            if on.voice.name == note_off.voice.name and int( on ) == int( note_off ):
                # print( note_off, i, [ str(v) for v in self.active_notes ] )
                match_index = i

        if match_index != None:
            del self.active_notes[ match_index ]
            # self.active_notes = list( self.active_notes )

    def process ( self, event ):
        if isinstance( event, NoteOnEvent ):
            self.activate( event )
        elif isinstance( event, NoteOffEvent ):
            self.deactivate( event )

    def close ( self, time : int ):
        for on in self.active_notes:
            print( on )
            yield on.note_off( time )

def balance_notes ( events, get_time : Callable ):
    tracker = NoteTracker()

    for event in events:
        tracker.process( event )

        yield event

    for event in tracker.close( get_time() ):
        yield event

async def balance_notes_async ( events, get_time : Callable ):
    tracker = NoteTracker()

    async for event in events:
        tracker.process( event )

        yield event

    for event in tracker.close( get_time() ):
        yield event