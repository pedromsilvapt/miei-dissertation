from musikla.core.events import MusicEvent, VoiceEvent, ContextChangeEvent, NoteEvent, RestEvent, BarNotationEvent, StaffNotationEvent
from musikla.core import MusicBuffer, Voice
from .transformer import Transformer
from typing import Tuple, Dict
from fractions import Fraction

TimeSignature = Tuple[int, int]

class VoiceNotationInfo:
    def __init__ ( self, name : str, time_signature : TimeSignature, bars_per_staff : int, beats_per_bar : int ):
        self.name : str = name
        self.time_signature = time_signature
        self.bars_per_staff = bars_per_staff
        self.beats_per_bar = beats_per_bar
        self._beat_value : Fraction = None

        self.beats_count : float = 0
        self.bars_count : int = 0

    @property
    def is_staff_full ( self ) -> bool:
        return self.bars_count >= self.bars_per_staff and self.is_bar_full

    @property
    def is_bar_full ( self ) -> bool:
        return self.beats_count >= self.beats_per_bar

    @property
    def beat_value ( self ) -> Fraction:
        if self._beat_value is None:
            ( u, l ) = self.time_signature

            if u >= 6 and u % 3 == 0:
                self._beat_value = Fraction( 3, 2 * l )
            else:
                self._beat_value = Fraction( 1, l )

        return self._beat_value

    def voice_value_to_beats ( self, voice : Voice, value ) -> float:
        return value / self.beat_value
    
    def beats_to_voice_value ( self, beats, voice : Voice ) -> float:
        return beats * self.beat_value

    def split_value ( self, voice : Voice, value ):
        if self.is_bar_full:
            yield 0, 0, False

        event_beats = self.voice_value_to_beats( voice, value )

        leftovers = self.beats_per_bar - self.beats_count

        if event_beats <= leftovers:
            yield value, voice.get_duration_absolute( voice.value ), True

            self.beats_count += event_beats
        else:
            while event_beats > leftovers:
                sub_value = self.beats_to_voice_value( leftovers, voice )
                
                sub_duration = voice.get_duration_absolute( sub_value )

                yield sub_value, sub_duration, False
                
                self.beats_count += leftovers

                event_beats -= leftovers

                leftovers = self.beats_per_bar - self.beats_count

            sub_value = self.beats_to_voice_value( event_beats, voice )
                
            sub_duration = voice.get_duration_absolute( sub_value )

            yield sub_value, sub_duration, True

            self.beats_count += event_beats

    def new_staff ( self ):
        self.bars_count = 0
        self.beats_count = 0

    def new_bar ( self ):
        self.bars_count += 1
        self.beats_count = 0

    def transform ( self, event : MusicEvent ):
        if isinstance( event, RestEvent ) or isinstance( event, NoteEvent ):
            # Analyze how much duration this measure has left, and if necessary, split up the rest event into two
            # And then pass them along through the `self.add_output` method
            timestamp = event.timestamp

            for sub_value, sub_duration, is_last in self.split_value( event.voice, event.value ):
                if self.is_staff_full:
                    self.new_staff()

                    yield StaffNotationEvent( timestamp, event.voice )
                elif self.is_bar_full:
                    self.new_bar()

                    yield BarNotationEvent( timestamp, event.voice )

                if sub_value > 0:
                    if isinstance( event, RestEvent ):
                        yield event.clone( timestamp = timestamp, value = sub_value, duration = sub_duration )
                    else:
                        # Keep track of the length of the notes that are played and when a new measure needs to be added
                        # Also analyze how much duration this measure has left, and if necessary, split up the note event into two
                        # and mark the first part of it as `tied`, so that the it is known the next note is to be played continuously
                        yield event.clone( timestamp = timestamp, value = sub_value, duration = sub_duration, tied = not is_last )

                    timestamp += sub_duration
        else:
            yield event


class AnnotateTransformer(Transformer):
    """
    This transformer expects composed notes. Also this transformer expects that note events are either contiguous,
    or separated by rest events for each voice. If that is not the case, yout can use the voice identifier transformer before this one.
    """
    def __init__ ( self, time_signature : TimeSignature = None, beats_per_staff : int = 12 ):
        super().__init__()

        self.time_signature : TimeSignature = time_signature
        self.beats_per_staff : int = beats_per_staff
        self.voices : Dict[str, VoiceNotationInfo] = {}
        self.buffered_events : MusicBuffer = MusicBuffer()
        
    @property
    def bars_per_staff ( self ) -> int:
        return 16 / self.time_signature[ 1 ]

    @property
    def beats_per_bar ( self ) -> int:
        return int( self.beats_per_staff / self.bars_per_staff )

    def get_voice_for ( self, event : VoiceEvent ) -> VoiceNotationInfo:
        name = event.voice.name
        
        if name not in self.voices:
            self.voices[ name ] = VoiceNotationInfo( name, self.time_signature, self.bars_per_staff, self.beats_per_bar )
        
        return self.voices[ name ]

    def transform ( self ):
        while True:
            done, event = yield

            if done: break

            if self.time_signature is None and isinstance( event, ContextChangeEvent ) and event.property == 'timeSignature':
                self.time_signature = event.value

            if self.time_signature is None and isinstance( event, VoiceEvent ):
                self.time_signature = event.voice.time_signature
                
            for buffered_event in self.buffered_events.collect( event.timestamp ):
                self.add_output( buffered_event )

            if isinstance( event, VoiceEvent ):
                voice_info = self.get_voice_for( event )

                # Transform this event and possibly create any others that might be needed
                # Note that instead of emitting them forward immediately, we add them to the buffer
                # This is because some of them might have timestamps in the future, and all the events must be propertly sorted
                # This means that we have to wait for the next inputs before being sure we can emit the new ones
                for ev in voice_info.transform( event ):
                    self.buffered_events.append( ev )
            else:
                self.add_output( event )

        for buffered_event in self.buffered_events.collect():
            self.add_output( buffered_event )




