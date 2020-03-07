from musikla.core.events import MusicEvent
from musikla.core.events.transformers import Transformer
from typing import Iterable

class Sequencer:
    def __init__ ( self ):
        self.realtime = False

        self.transformer : Transformer = None

    def set_transformers ( self, *transformers : Transformer ):
        self.transformer = Transformer.pipeline( 
            *transformers,
            Transformer.subscriber( self.on_event, self.on_close )
        )

    @property
    def playing ( self ) -> bool:
        raise BaseException( "Abstract property Sequencer.playing accessed." )

    def get_time ( self ) -> int:
        raise BaseException( "Abstract method Sequencer.get_time called." )

    def on_event ( self, event : MusicEvent ):
        raise BaseException( "Abstract method Sequencer.on_event called." )
    
    def on_close ( self ):
        raise BaseException( "Abstract method Sequencer.on_close called." )

    def register_event ( self, event : MusicEvent ):
        if self.transformer is None:
            self.on_event( event )
        else:
            self.transformer.add_input( event )

    def register_events_many ( self, events : Iterable[MusicEvent] ):
        for event in events:
            self.register_event( event )

    def join ( self ):
        raise BaseException( "Abstract method Sequencer.join called." )

    def start ( self ):
        raise BaseException( "Abstract method Sequencer.start called." )

    def close ( self ):
        if self.transformer is None:
            self.on_close()
        else:
            self.transformer.end_input()
