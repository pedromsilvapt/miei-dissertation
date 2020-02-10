from musikla.core.events import MusicEvent, NoteEvent, ProgramChangeEvent
from ..sequencer import Sequencer
from .builder import ABCBuilder
import time

def get_milliseconds () -> int:
    return int( round( time.time() * 1000 ) )

class ABCSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.start_time : int = None
        self.file_builder : ABCBuilder = ABCBuilder()
        self.filename : str = filename
    
    @property
    def playing ( self ) -> bool:
        return False
        
    def get_time ( self ):
        if self.start_time == None:
            return 0
        
        return get_milliseconds() - self.start_time

    def register_event ( self, event : MusicEvent, now = None ):
        self.file_builder.add_event( event )

    def register_events_many ( self, events, now = None ):
        if now == None:
            now = self.get_time()
        
        for event in events:
            self.register_event( event, now = now )

    def join ( self ):
        pass

    def start ( self ):
        self.start_time = get_milliseconds()
        
    def close ( self ):
        with open( self.filename, 'w' ) as f:
            file = self.file_builder.build()

            f.write( str( file ) )
            
            f.flush()

        
