from .instrument import Instrument
from copy import copy

class Voice:
    unknown : 'Voice' = None

    def __init__ ( self, 
                   name : str, 
                   instrument : Instrument,
                   time_signature : (int, int) = (4, 4),
                   velocity : int = 127,
                   octave : int = 4,
                   value : float = 1,
                   tempo : int = 60
                 ):
        self.id : int = id( self )
        self.name : str = name
        self.instrument : Instrument = instrument
        self.time_signature : (int, int) = time_signature
        self.velocity : int = velocity
        self.octave : int = octave
        self.value : float = value
        self.tempo : int = tempo

    def clone ( self,
                name : str = None, 
                instrument : Instrument = None,
                time_signature : (int, int) = None,
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

    def get_value ( self, value : float ) -> float:
        if value == None:
            return self.value
        else:
            return self.value * value

    def get_duration_ratio ( self ) -> float:
        ( u, l ) = self.time_signature

        if u >= 6 and u % 3 == 0:
            return 3 / l
        else:
            return 1 / l

    def get_duration ( self, value : float = None ) -> int:
        beat_duration = 60 / self.tempo

        whole_note_duration = beat_duration * 1000.0 / self.get_duration_ratio()

        return int( whole_note_duration * self.get_value( value ) )

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
