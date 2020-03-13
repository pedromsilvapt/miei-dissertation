import time
from .sequencers import Sequencer, SequencerFactory
from musikla.core import Context
from configparser import ConfigParser
from typing import List, Any, Optional, Union

def get_milliseconds () -> int:
    return int( round( time.time() * 1000 ) )

class Player():
    def __init__ ( self, sequencers : List[Sequencer] = [], events = [] ):
        self.events = events
        self.sequencers : List[Sequencer] = sequencers
        self.started : bool = False
        self.start_time : Optional[int] = None
        self.print_events = False
        
        self.sequencer_factories : List[SequencerFactory] = []

    def add_sequencer_factory ( self, factory : Any, context : Context, config : ConfigParser ):
        self.sequencer_factories.append( factory( context, config ) )

    def make_sequencer ( self, uri : str ) -> Sequencer:
        default : Optional[SequencerFactory] = None
        
        sequencer : Optional[Sequencer] = None

        for factory in self.sequencer_factories:
            if factory.default:
                default = factory
            else:
                sequencer = factory.from_str( uri )

            if sequencer != None: break

        if sequencer is None and default is not None:
            sequencer = default.from_str( uri )
        
        if sequencer is None:
            raise Exception( f"Could not create a sequencer for { uri }" )

        return sequencer

    def add_sequencer ( self, sequencer : Union[Sequencer, str] ):
        if type( sequencer ) is str:
            sequencer = self.make_sequencer( sequencer )

        self.sequencers.append( sequencer )


    @property
    def realtime ( self ) -> bool:
        return any( seq.realtime for seq in self.sequencers )

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

    def play_more ( self, events ):
        if not self.started:
            self.setup()

        events = list( events )

        if self.print_events and events:
            print( 'playing', events[ 0 ].timestamp, ' '.join( str( e ) for e in events ) )

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
