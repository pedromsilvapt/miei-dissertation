from .instrument import Instrument
from .shared_context import SharedContext
from .symbols_scope import SymbolsScope

class Library:
    def on_link ( self, context ):
        pass

class Context():
    def __init__ ( self, 
                   shared = SharedContext(), 
                   time_signature = ( 4, 4 ),
                   channel = 0,
                   velocity = 127,
                   octave = 4,
                   value = 1 / 4,
                   tempo = 120,
                   cursor = 0,
                   symbols = SymbolsScope(),
                   instruments = list()
                 ):
        self.shared = shared
        self.time_signature = time_signature
        self.channel = channel
        self.velocity = velocity
        self.octave = octave
        self.value = value
        self.tempo = tempo
        self.cursor = cursor
        self.symbols = symbols

        for instrument in instruments:
            self.symbols.assign_instrument( instrument )
    
    def fork ( self, cursor = None, symbols = None ):
        return Context(
            shared = self.shared,
            time_signature = self.time_signature,
            channel = self.channel,
            octave = self.octave,
            velocity = self.velocity,
            value = self.value,
            tempo = self.tempo,
            cursor = self.cursor if cursor == None else cursor,
            symbols = self.symbols if symbols == None else symbols
        )

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

    def link ( self, library : Library ):
        library.on_link( self )
