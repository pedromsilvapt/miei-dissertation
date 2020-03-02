from musikla.core.events import MusicEvent, VoiceEvent
from .transformer import Transformer
from typing import List, Dict, Union

class EnsureOrderTransformer(Transformer):
    def __init__ ( self, label : str = None, total_order : bool = True ):
        super().__init__()
        
        self.label : str = label
        self.total_order : bool = total_order

        self.last_timestamp : int = 0
        self.voices : Dict[str, int] = {}

    def print_warning ( self, event : MusicEvent ):
        print( f"{self.label}: { event.timestamp } < { self.last_timestamp } { event.__dict__ }" )

    def print_warning_voice ( self, event : MusicEvent ):
        print( f"{self.label} [{ event.voice.name }]: { event.timestamp } < { self.last_timestamp } { event.__dict__ }" )

    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if self.total_order or not isinstance( event, VoiceEvent ):
                if event.timestamp < self.last_timestamp:
                    self.print_warning( event )
                else:
                    self.last_timestamp = event.timestamp
            else:
                if event.voice.name not in self.voices:
                    self.voices[ event.voice.name ] = 0
                
                if event.timestamp < self.voices[ event.voice.name ]:
                    self.print_warning_voice( event )
                else:
                    self.voices[ event.voice.name ] = event.timestamp
            
            self.add_output( event )
        
        self.end_output()


