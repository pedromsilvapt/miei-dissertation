from typing import Tuple, Union
from .instrument import Instrument
from fractions import Fraction
from copy import copy

class Voice:
    unknown : 'Voice' = None

    def __init__ ( self, 
                   name : str, 
                   instrument : Instrument,
                   time_signature : Tuple[int, int] = (4, 4),
                   velocity : int = 127,
                   octave : int = 4,
                   value : float = 1,
                   tempo : int = 60
                 ):
        self.id : int = id( self )
        self.name : str = name
        self.instrument : Instrument = instrument
        self.time_signature : Tuple[int, int] = time_signature
        self.velocity : int = velocity
        self.octave : int = octave
        self.value : float = value
        self.tempo : int = tempo

    def clone ( self,
                name : str = None, 
                instrument : Instrument = None,
                time_signature : Tuple[int, int] = None,
                velocity : int = None,
                octave : int = None,
                value : float = None,
                tempo : int = None ):
        return Voice(
            name = self.name if name is None else name,
            instrument = self.instrument if instrument is None else instrument,
            time_signature = self.time_signature if time_signature is None else time_signature,
            velocity = self.velocity if velocity is None else velocity,
            octave = self.octave if octave is None else octave,
            value = self.value if value is None else value,
            tempo = self.tempo if tempo is None else tempo
        )

    def revoice ( self, event ):
        if event.voice == self:
            return event

        event = event.clone()

        if self.octave != event.voice.octave:
            event.octave = event.octave - event.voice.octave + self.octave

        if self.velocity != event.voice.velocity:
            event.velocity = self.velocity

        event.voice = self

        return event

    def get_value ( self, value : float = None ) -> float:
        if value == None:
            return self.value
        else:
            return self.value * value

    def get_relative_value ( self, value : Union[float, Fraction] ) -> Fraction:
        if not isinstance( value, Fraction ):
            value = Fraction( value )

        return value / self.value

    def get_duration_ratio ( self ) -> float:
        ( u, l ) = self.time_signature

        if u >= 6 and u % 3 == 0:
            return 1.5 / l
        else:
            return 1 / l

    def get_duration ( self, value : float = None ) -> int:
        """Transform a not value into the real world milliseconds it takes, according to the voice's tempo and time signature"""
        return self.get_duration_absolute( self.get_value( value ) )

    def get_beat_duration ( self ) -> int:
        return int( 60 / self.tempo )

    def get_duration_absolute ( self, value : float = None ) -> int:
        beat_duration = 60 / self.tempo

        whole_note_duration = beat_duration * 1000.0 / self.get_duration_ratio()

        return int( whole_note_duration * value )

    def from_duration ( self, milliseconds : int, max_denominator : int = 32 ) -> Fraction:
        """Transform a duration in milliseconds to an approximated note value relative to the tempo and time signature and default not length"""
        return self.get_relative_value( self.from_duration_absolute( milliseconds, max_denominator ) )
        
    def from_duration_absolute ( self, milliseconds : int, max_denominator : int = 32 ) -> Fraction:
        """Transform a duration in milliseconds to an approximated note value relative to the tempo and time signature"""
        beat_duration = 60 / self.tempo

        whole_note_duration = beat_duration * 1000.0 / self.get_duration_ratio()
        
        return Fraction( milliseconds / whole_note_duration ).limit_denominator( max_denominator )

    def __eq__ ( self, other ):
        if not isinstance( other, Voice ): return False

        return  self.name == other.name \
            and self.instrument == other.instrument \
            and self.time_signature == other.time_signature \
            and self.velocity == other.velocity \
            and self.octave == other.octave \
            and self.value == other.value \
            and self.tempo == other.tempo

Voice.unknown = Voice( "(unknown)", None )
