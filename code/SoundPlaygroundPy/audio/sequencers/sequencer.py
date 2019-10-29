from core.events import MusicEvent
from typing import Iterable

class Sequencer:
    def __init__ ( self ):
        pass

    @property
    def playing ( self ) -> bool:
        raise BaseException( "Asbtract property Sequencer.playing accessed." )

    def register_event ( self, event : MusicEvent ):
        raise BaseException( "Asbtract method Sequencer.register_event called." )

    def register_events_many ( self, events : Iterable[MusicEvent] ):
        raise BaseException( "Asbtract method Sequencer.register_events_many called." )

    def join ( self ):
        raise BaseException( "Asbtract method Sequencer.join called." )

    def start ( self ):
        raise BaseException( "Asbtract method Sequencer.start called." )

    def close ( self ):
        raise BaseException( "Asbtract method Sequencer.close called." )
