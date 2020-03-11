from .transformer import Transformer
from musikla.core import Voice
from musikla.core.events import MusicEvent, NoteEvent, RestEvent, ChordEvent
from typing import List

class SlidingAverage():
    def __init__ ( self ):
        self.sum : float = 0
        self.count : int = 0

    def __iadd__ ( self, value : float ):
        if self.count == 0:
            self.sum = value
            self.count = 1
        else:
            #  ( ( self.average / self.count ) + ( value / ( self.count + 1 ) ) )
            self.sum += value
            self.count += 1

        return self

    def __int__ ( self ):
        if self.count == 0:
            return 0

        return int( self.sum / self.count )
        
    def __float__ ( self ):
        if self.count == 0:
            return 0

        return float( self.sum / self.count )

class VoiceIdentifierVoice():
    def __init__ ( self, transformer : 'NotationBuilderTransformer', parent : Voice, index : int ):
        self.transformer : VoiceIdentifierVoice = transformer
        self.parent_name : str = parent.name
        self.voice : Voice = parent.clone( parent.name + '/' + str( index ) )
        self.index = index
        self.average_pitch : SlidingAverage = SlidingAverage()
        self.auto_create_rests : bool = True
        self.auto_create_end_rests : bool = True
        self.last_event : MusicEvent = None

    @property
    def last_timestamp ( self ):
        if not self.last_event:
            return 0

        return self.last_event.timestamp
    
    @property
    def last_end_timestamp ( self ):
        if not self.last_event:
            return 0

        return self.last_event.end_timestamp

    def is_busy_at ( self, timestamp : int ) -> bool:
        return self.last_end_timestamp > timestamp

    def is_connected_at ( self, timestamp : int ) -> bool:
        return abs( timestamp - self.last_end_timestamp ) <= 3

    def distance ( self, event : NoteEvent ) -> float:
        return abs( int( event ) - int( self.average_pitch ) )

    def create_rest ( self, target : int, visible : bool = True ) -> RestEvent:
        duration = target - self.last_end_timestamp

        value = self.voice.from_duration_absolute( duration )

        return RestEvent(
            timestamp = self.last_end_timestamp,
            visible = visible,
            duration = duration,
            value = value,
            voice = self.voice
        )

    def append ( self, *events : MusicEvent ):
        for event in events:
            if isinstance( event, NoteEvent ):
                self.average_pitch += int( event )

                # TODO Allow setting a minimum rest duration. If the empty space between the events is less than
                # said minimum, then no rest is created
                if self.auto_create_rests and self.last_end_timestamp < event.timestamp - 1:
                    self.transformer.add_output( self.create_rest( event.timestamp ) )

            self.transformer.add_output( event.clone( voice = self.voice ) )

        self.last_event = event

class VoiceIdentifierTransformer(Transformer):
    """
    This class receives a flat, ordered stream of musical events and splits them in multiple voices and identifies parallel notes/chords
    """
    def __init__ ( self, auto_create_rests : bool = True, auto_create_end_rests : bool = True ):
        super().__init__()

        self.voices : List[VoiceIdentifierVoice] = []

        self.auto_create_rests : bool = auto_create_rests
        
        self.auto_create_end_rests : bool = auto_create_end_rests
    
    def create_voice_for ( self, event : NoteEvent ) -> VoiceIdentifierVoice:
        index = max( ( voice.index for voice in self.voices if voice.parent_name == event.voice.name ), default = 0 )

        voice = VoiceIdentifierVoice( self, event.voice, index + 1 )

        voice.auto_create_rests = self.auto_create_rests
        voice.auto_create_end_rests = self.auto_create_end_rests

        self.voices.append( voice )

        return voice

    def find_voice_for ( self, event, auto_create : bool = True ) -> VoiceIdentifierVoice:
        best_voice, best_voice_dst = None, None

        for voice in self.voices:
            if voice.parent_name != event.voice.name:
                continue

            # If the voice already has a sound playing at this timestamp
            if voice.is_busy_at( event.timestamp ):
                continue

            voice_dst = voice.distance( event )

            if best_voice is None or best_voice_dst > voice_dst:
                best_voice = voice
                best_voice_dst = voice_dst

        if best_voice is None and auto_create:
            best_voice = self.create_voice_for( event )
        
        return best_voice
    
    def find_voice_for_rest ( self, event, auto_create : bool = True ) -> VoiceIdentifierVoice:
        for voice in self.voices:
            if voice.parent_name != event.voice.name:
                continue

            # If the voice already has a sound playing at this timestamp
            if voice.is_connected_at( event.timestamp ):
                return voice

        return self.create_voice_for( event )

    def register_rest ( self, event : RestEvent ):
        voice = self.find_voice_for_rest( event )

        voice.append( event )       

    def register_note ( self, event : NoteEvent ):
        voice = self.find_voice_for( event )

        voice.append( event )
    
    def register_chord ( self, event : ChordEvent ):
        voice = self.find_voice_for( event )

        voice.append( event )

    def transform ( self ):
        """
        For now, NoteOn/NoteOff events will be ignored. 
        Use the compose transformer before passing events into this notation builder. 
        This might change in the future.
        """
        while True:
            done, event = yield

            if done: break

            if isinstance( event, NoteEvent ):
                self.register_note( event )
            elif isinstance( event, RestEvent ):
                self.register_rest( event )
            else:
                self.add_output( event )

        if self.auto_create_end_rests and self.voices:
            last_voice_timestamp : int = max( [ voice.last_end_timestamp for voice in self.voices ] )

            for voice in self.voices:
                if voice.last_end_timestamp < last_voice_timestamp:
                    self.add_output( voice.create_rest( last_voice_timestamp, visible = False ) )
