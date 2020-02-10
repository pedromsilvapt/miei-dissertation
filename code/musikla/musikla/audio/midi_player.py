import time
from .sequencers import Sequencer
from typing import List

def get_milliseconds () -> int:
    return int( round( time.time() * 1000 ) )

class MidiPlayer():
    def __init__ ( self, sequencers : List[Sequencer] = [], events = [] ):
        self.events = events
        self.sequencers : List[Sequencer] = sequencers
        self.started : bool = False
        self.start_time : int = None
        self.print_events = False
    
    def setup ( self ):
        for seq in self.sequencers:
            seq.start()

        self.start_time = get_milliseconds()

        self.started = True

    def get_time ( self ):
        if not self.started:
            return 0
        
        return get_milliseconds() - self.start_time

    def play ( self ):
        if not self.started:
            self.setup()

        for seq in self.sequencers:
            seq.register_events_many( self.events )

    def play_more ( self, events, now : int = None ):
        if not self.started:
            self.setup()

        events = list( events )

        if self.print_events and events:
            print( 'playing', ( now or 0 ) + events[ 0 ].timestamp, ' '.join( str( e ) for e in events ) )

        for seq in self.sequencers:
            seq.register_events_many( events, now )
            
    def join ( self ):
        if not self.started:
            return

        for seq in self.sequencers:
            seq.join()

    def close ( self ):
        if self.started:
            for seq in self.sequencers:
                seq.close()