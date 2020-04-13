from musikla.core.music import MusicBuffer
from .transformer import Transformer

class SortTransformer(Transformer):
    def __init__ ( self, window_size : int = 0 ):
        self.buffer : MusicBuffer = MusicBuffer()
        self.window_size : int = window_size
        self.last_timestamp : int = 0

    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if self.window_size == 0:
                self.add_output( event )
            else:
                self.buffer.append( event )

                if event.timestamp > self.last_timestamp:
                    self.last_timestamp = event.timestamp

                    for ev in self.buffer.collect( self.last_timestamp - self.window_size ):
                        self.add_output( ev )
                    
        for ev in self.buffer.collect():
            self.add_output( ev )
        
        self.end_output()


