from typing import List
from .transformer import Transformer
from ..note import NoteEvent

class TerminationMelodyTransformer(Transformer):
    def __init__ ( self, events, exclude_matches : bool = True, stop_on_match : bool = True ):
        super().__init__()

        self.pattern = [ ev for ev in events if isinstance( ev, NoteEvent ) ]
        self.exclude_matches : bool = True
        self.stop_on_match : bool = stop_on_match
        self.matching_now : bool = False
        self.matched : bool = False

    def transform ( self ):
        buffer = []

        while True:
            done, event = yield

            if done: break

            if isinstance( event, NoteEvent ):
                buffer.append( BufferSlot( event ) )

                while len( buffer ) > len( self.pattern ):
                    for ev in buffer.pop( 0 ): self.add_output( ev )

                if len( buffer ) == len( self.pattern ):
                    matched = True

                    for i in range( len( self.pattern ) ):
                        if int( self.pattern[ i ] ) != int( buffer[ i ].event ):
                            matched = False

                            break
                    
                    self.matching_now = matched

                    if matched:
                        self.matched = True
                        
                        if not self.exclude_matches:
                            for slot in buffer:
                                for ev in slot:
                                    self.add_output( ev )
                        
                            buffer = []
                        
                        
                        if self.stop_on_match:
                            buffer = []

                            self.end_output()
            elif buffer:
                buffer[ -1 ].append( event )
            else:
                self.add_output( event )
            
        for slot in buffer:
            for ev in slot:
                self.add_output( ev )

class BufferSlot:
    def __init__ ( self, event ):
        self.event = event
        self.next_events : List = None
    
    def append ( self, event ):
        if not self.next_events:
            self.next_events = []

        self.next_events.append( event )

    def __iter__ ( self ):
        yield self.event

        if self.next_events:
            for event in self.next_events:
                yield event
