import time
from .sequencers import Sequencer, SequencerFactory
from musikla.core import Context
from configparser import ConfigParser
from argparse import Namespace
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

    def make_sequencer_from_format ( self, format : str, uri : str, args : List[str] = [] ) -> Sequencer:
        factory : Optional[SequencerFactory] = None

        for f in self.sequencer_factories:
            if f.name == format:
                factory = f
                break
        
        if factory is None:
            raise Exception( f"Could not create a sequencer for format { format }" )

        if factory.argparser is not None:
            arguments = factory.argparser.parse_args( args )
        else:
            arguments = args

        sequencer = factory.from_str( uri, arguments )

        if sequencer is None:
            raise Exception( f"Could not create a sequencer format { format } for { uri }" )

        return sequencer

    def make_sequencer_from_uri ( self, uri : str, args : List[str] = [] ) -> Sequencer:
        default : Optional[SequencerFactory] = None
        
        sequencer : Optional[Sequencer] = None

        for factory in self.sequencer_factories:
            if factory.default:
                if default is not None:
                    print( f"WARNING: Replacing default sequencer { default.__class__.__name__ } with { factory.__class__.__name__ }" )
                    
                default = factory
            else:
                if factory.argparser is not None:
                    arguments = factory.argparser.parse_args( args )
                else:
                    arguments = args

                sequencer = factory.from_str( uri, arguments )

            if sequencer != None: break

        if sequencer is None and default is not None:
            if default.argparser is not None:
                arguments = default.argparser.parse_args( args )
            else:
                arguments = args

            sequencer = default.from_str( uri, arguments )
        
        if sequencer is None:
            raise Exception( f"Could not create a sequencer for { uri }" )

        return sequencer

    def add_sequencer ( self, sequencer : Union[Sequencer, str] ):
        if type( sequencer ) is str:
            sequencer = self.make_sequencer_from_uri( sequencer )

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
