from typing import Optional
from musikla.core.events.transformers import Transformer, ComposeNotesTransformer, ComposeChordsTransformer, VoiceIdentifierTransformer, AnnotateTransformer, EnsureOrderTransformer
from musikla.core.events import MusicEvent, NoteEvent, ProgramChangeEvent
from musikla.core import Clock
from ..sequencer import Sequencer, SequencerFactory
from .builder import ABCBuilder
from pathlib import Path

class ABCSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.file_builder : ABCBuilder = ABCBuilder()
        self.filename : str = filename
        self.clock : Clock = Clock( auto_start = False )

        self.set_transformers(
            # EnsureOrderTransformer( 'beforeCompose' ),
            ComposeNotesTransformer(),
            ComposeChordsTransformer(),
            # EnsureOrderTransformer( 'afterCompose' ),
            VoiceIdentifierTransformer(),
            # EnsureOrderTransformer( 'afterIdentify', False ),
            AnnotateTransformer()
        )
    
    @property
    def playing ( self ) -> bool:
        return False
        
    def get_time ( self ):
        if not self.clock.started:
            return 0

        return self.clock.elapsed()

    def on_event ( self, event : MusicEvent ):
        self.file_builder.add_event( event )

    def on_close ( self ):
        if self.filename is not None:
            with open( self.filename, 'w' ) as f:    
                file = self.file_builder.build()

                f.write( str( file ) )
                
                f.flush()

    def join ( self ):
        pass

    def start ( self ):
        self.clock.start()

class ABCSequencerFactory( SequencerFactory ):
    def from_str ( self, uri : str ) -> Optional[ABCSequencer]:
        suffix = ( Path( uri ).suffix or '' ).lower()

        if suffix == '.abc':
            return ABCSequencer( uri )