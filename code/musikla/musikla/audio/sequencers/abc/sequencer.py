from musikla.core.events.transformers import Transformer, ComposeNotesTransformer, VoiceIdentifierTransformer, AnnotateTransformer, EnsureOrderTransformer
from musikla.core.events import MusicEvent, NoteEvent, ProgramChangeEvent
from musikla.core import Clock
from ..sequencer import Sequencer
from .builder import ABCBuilder
import time

class ABCSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.file_builder : ABCBuilder = ABCBuilder()
        self.filename : str = filename
        self.clock : Clock = Clock( auto_start = False )

        self.pipeline = Transformer.pipeline(
            # EnsureOrderTransformer( 'beforeCompose' ),
            ComposeNotesTransformer(),
            # EnsureOrderTransformer( 'afterCompose' ),
            VoiceIdentifierTransformer(),
            # EnsureOrderTransformer( 'afterIdentify', False ),
            AnnotateTransformer(),
            Transformer.subscriber( self._register_event, self._close )
        )
    
    @property
    def playing ( self ) -> bool:
        return False
        
    def get_time ( self ):
        if not self.clock.started:
            return 0

        return self.clock.elapsed()

    def _register_event ( self, event : MusicEvent ):
        self.file_builder.add_event( event )

    def _close ( self ):
        with open( self.filename, 'w' ) as f:
            file = self.file_builder.build()

            print( str( file ) )

            f.write( str( file ) )
            
            f.flush()

    def register_event ( self, event : MusicEvent, now = None ):
        self.pipeline.add_input( event )

    def register_events_many ( self, events, now = None ):
        if now == None:
            now = self.get_time()
        
        for event in events:
            self.register_event( event, now = now )

    def join ( self ):
        pass

    def start ( self ):
        self.clock.start()
        
    def close ( self ):
        self.pipeline.end_input()

        
