from .instrument import Instrument
from .shared_context import SharedContext

class Context():
    def __init__ ( self ):
        self.shared = SharedContext()
        self.time_signature = ( 4, 4 )
        self.channel = 0
        self.velocity = 120
        self.octave = 4
        self.value = 1 / 4
        self.tempo = 120
        self.cursor = 0
        self.instruments = dict()

    def add_instrument ( self, name, program ):
        instrument = Instrument( name, program, None )

        self.instruments[ name ] = instrument

        return instrument
    
    def fork ( self ):
        context = Context()

        context.shared = self.shared
        context.instruments = dict( self.instruments )
        context.time_signature = self.time_signature
        context.channel = self.channel
        context.velocity = self.velocity
        context.value = self.value
        context.tempo = self.tempo
        context.cursos = self.cursor

        return context

    def join ( self, *child_context ):
        for context in child_context:
            if context.cursor > self.cursor:
                self.cursor = context.cursor
    
    def get_duration_ratio ( self ):
        ( u, l ) = self.time_signature

        if u >= 6 and u % 3 == 0:
            return 3 / l
        else:
            return 1 / l

    def get_duration ( self, value ):
        beat_duration = 60 / self.tempo

        whole_note_duration = beat_duration * 1000.0 / self.get_duration_ratio()

        return int( whole_note_duration * value )
