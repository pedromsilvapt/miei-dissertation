from musikla.core.events import MusicEvent
from musikla.core import Voice
from .transformer import Transformer
from typing import List, Tuple

def find ( arr, predicate, default_value = None ):
    for elem in arr:
        if predicate( elem ):
            return elem

    return default_value

class NotationBuilderTransformer(Transformer):
    def to_string ( self, events_per_voice : List[Tuple[Voice, List[MusicEvent]]] ) -> str:
        return None
    
    def transform ( self ):
        events_per_voice : List[Tuple[Voice, List[MusicEvent]]] = []

        while True:
            done, event = yield

            if done: break

            name = event.voice.name

            voice_events = find( events_per_voice, lambda pair: pair[ 0 ] == name )

            if voice_events is None:
                voice_events = ( name, [] )

                events_per_voice.append( voice_events )

            voice_events[ 1 ].append( event )

            self.add_output( self.to_string( events_per_voice ) )
    
class MusiklaNotationBuilderTransformer(NotationBuilderTransformer):
    def voice_to_string ( self, voice : Tuple[Voice, List[MusicEvent]] ) -> str:
        return f":{voice[ 0 ].name} " + ' '.join( map( str, voice[ 1 ] ) )
    
    def to_string ( self, events_per_voice : List[Tuple[Voice, List[MusicEvent]]] ) -> str:
        l = len( events_per_voice )

        if l == 0:
            return ""
        elif l == 1:
            return self.voice_to_string( events_per_voice[ 0 ] )
        else:
            return '(\n\t  ' + '\n\t| '.join( map( lambda v: self.voice_to_string( v ), events_per_voice ) ) + '\n)'
