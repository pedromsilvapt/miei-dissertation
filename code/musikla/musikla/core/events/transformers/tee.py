from .transformer import Transformer
from typing import List, Union

class TeeTransformer(Transformer):
    def __init__ ( self, sinks : Union[Transformer, List[Transformer]] = [] ):
        if isinstance( sinks, Transformer ):
            self.sinks : List[Transformer] = [ sinks ]
        else:
            self.sinks : List[Transformer] = sinks


    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            for sink in self.sinks:
                sink.add_input( event )
            
            self.add_output( event )
        
        for sink in self.sinks:
            sink.end_input()
        
        self.end_output()


