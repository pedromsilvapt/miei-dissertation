from .instrument import Instrument
from .shared_context import SharedContext
from .symbols_scope import SymbolsScope
from typing import List, Hashable

class Library:
    def __init__ ( self, namespace : str = None ):
        self.namespace : str = namespace
        self.context : 'Context' = None

    def on_link ( self ):
        pass

    def resolve ( self, name : str ) -> str:
        if self.namespace != None and self.namespace != '':
            if self.namespace.endswith( '\\' ) and name.startswith( '\\' ):
                return self.namespace + name[ 1: ]
            elif self.namespace.endswith( '\\' ) or name.startswith( '\\' ):
                return self.namespace + name
            else:
                return self.namespace + '\\' + name
        else:
            return name

    def lookup ( self, name : Hashable, container : str = "", recursive : bool = True, follow_pointers : bool = True, default = None ):
        return self.context.symbols.lookup( self.resolve( name ), container = container, recursive = recursive, follow_pointers = follow_pointers, default = default )

    def assign ( self, name : Hashable, value, container = "", follow_pointers : bool = True ):
        return self.context.symbols.assign( self.resolve( name ), value, container, follow_pointers )

    def lookup_instrument ( self, name ):
        return self.context.symbols.lookup_instrument( self.resolve( name ) )

    def assign_instrument ( self, instrument ):
        self.assign( instrument.name, instrument, container = "instruments" )
        
        return instrument

    def lookup_internal ( self, name ):
        return self.context.symbols.lookup_internal( self.resolve( name ) )

    def assign_internal ( self, name, value ):
        self.context.symbols.assign_internal( self.resolve( name ), value )

class Context():
    def create ():
        return Context(
            instruments = [ Instrument( 'default', program = 1, channel = 0, ref_count = 1 ) ]
        )

    def __init__ ( self, 
                   shared : SharedContext = SharedContext(), 
                   time_signature : (int, int) = ( 4, 4 ),
                   channel : int = 0,
                   velocity : int = 127,
                   octave : int = 4,
                   value : float = 1,
                   tempo : int = 120,
                   cursor : int = 0,
                   symbols : SymbolsScope = SymbolsScope(),
                   instruments : List[Instrument] = list()
                 ):
        self.shared : SharedContext = shared
        self.time_signature : (int, int) = time_signature
        self.channel : int = channel
        self.velocity : int = velocity
        self.octave : int = octave
        self.value : float = value
        self.tempo : int = tempo
        self.cursor : int = cursor
        self.symbols : SymbolsScope = symbols

        for instrument in instruments:
            self.symbols.assign_instrument( instrument )
    
    def fork ( self, cursor : int = None, symbols : SymbolsScope = None ) -> 'Context':
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

    def is_linked ( self, library : Library ) -> bool:
        return self.symbols.lookup( library.__class__, container = 'libraries' ) != None

    def link ( self, library : Library ):
        if not self.is_linked( library ):
            library.context = self

            self.symbols.assign( library.__class__, library, container = "libraries" )

            library.on_link()

    def library ( self, library ) -> Library:
        return self.symbols.lookup( library, container = "libraries" )
