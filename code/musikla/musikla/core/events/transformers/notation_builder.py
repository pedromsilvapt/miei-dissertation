from musikla.core.events.event import MusicEvent
from musikla.core.voice import Voice
from .transformer import Transformer
from typing import List, Tuple

def find ( arr, predicate, default_value = None ):
    for elem in arr:
        if predicate( elem ):
            return elem

    return default_value

class NotationBuilderTransformer(Transformer):
    def __init__ ( self, only_final : bool = False ):
        super().__init__()

        self.only_final : bool = only_final

    def to_string ( self, events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] ) -> str:
        raise NotImplementedError()
    
    def transform ( self ):
        events_per_voice : List[Tuple[Voice, int, List[MusicEvent]]] = []

        while True:
            done, event = yield

            if done: break

            name = event.voice.name

            voice_events = find( events_per_voice, lambda pair: pair[ 0 ].name == name and pair[ 1 ] == event.staff )

            if voice_events is None:
                voice_events = ( event.voice, event.staff, [] )

                events_per_voice.append( voice_events )

            voice_events[ 2 ].append( event )

            if not self.only_final:
                self.add_output( self.to_string( events_per_voice ) )

        if self.only_final:
            self.add_output( self.to_string( events_per_voice ) )
