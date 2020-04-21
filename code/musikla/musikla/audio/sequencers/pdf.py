from musikla.audio.sequencers.abc.sequencer import ABCSequencer
from musikla.core.events import MusicEvent
from .sequencer import Sequencer, SequencerFactory
from typing import Optional
from pathlib import Path
from tempfile import gettempdir, gettempprefix

class PDFSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.filename : str = filename

        temp : str = f"{ gettempdir() }/{ gettempprefix() }-{ Path( filename ).name }.abc"

        self.abc_sequencer : ABCSequencer = ABCSequencer( temp )
    
    @property
    def playing ( self ):
        return self.abc_sequencer.playing
        
    def get_time ( self ):
        return self.abc_sequencer.get_time()

    def on_event ( self, event : MusicEvent ):
        self.abc_sequencer.register_event( event )
    
    def on_close ( self ):
        self.abc_sequencer.close()

    def join ( self ):
        pass

    def start ( self ):
        self.abc_sequencer.start()

class PDFSequencerFactory( SequencerFactory ):
    def init ( self ):
        self.name = 'pdf'

    def from_str ( self, uri : str, args ) -> Optional[PDFSequencer]:
        suffix = ( Path( uri ).suffix or '' ).lower()

        if suffix == '.pdf':
            return PDFSequencer( uri )
        
