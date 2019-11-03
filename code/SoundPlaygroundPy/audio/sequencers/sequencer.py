from core.events import MusicEvent
from typing import Iterable

class Sequencer:
    def __init__ ( self ):
        self.realtime = False

    @property
    def playing ( self ) -> bool:
        raise BaseException( "Abstract property Sequencer.playing accessed." )

    def get_time ( self ) -> int:
        raise BaseException( "Abstract method Sequencer.get_time called." )

    def register_event ( self, event : MusicEvent ):
        raise BaseException( "Abstract method Sequencer.register_event called." )

    def register_events_many ( self, events : Iterable[MusicEvent] ):
        raise BaseException( "Abstract method Sequencer.register_events_many called." )

    def join ( self ):
        raise BaseException( "Abstract method Sequencer.join called." )

    def start ( self ):
        raise BaseException( "Abstract method Sequencer.start called." )

    def close ( self ):
        raise BaseException( "Abstract method Sequencer.close called." )
