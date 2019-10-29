import time
import fluidsynth
from py_linq import Enumerable
from core.events import NoteEvent, RestEvent, ProgramChangeEvent
from .sequencers import Sequencer
from typing import List

class MidiPlayer():
    def __init__ ( self, sequencers : List[Sequencer] = [], events = [] ):
        self.events = events
        self.sequencers : List[Sequencer] = sequencers
        self.started = False
    
    def setup ( self ):
        for seq in self.sequencers:
            seq.start()

    def play ( self ):
        if not self.started:
            self.setup()

            self.started = True

        for seq in self.sequencers:
            seq.register_events_many( self.events )

    def play_more ( self, events ):
        if not self.started:
            self.setup()

            self.started = True

        for seq in self.sequencers:
            seq.register_events_many( events )
            

    def join ( self ):
        if not self.started:
            return

        for seq in self.sequencers:
            seq.join()

    def close ( self ):
        if self.started:
            for seq in self.sequencers:
                seq.close()
