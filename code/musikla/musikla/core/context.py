from .instrument import Instrument, GeneralMidi
from .voice import Voice
from .shared_context import SharedContext
from .symbols_scope import SymbolsScope
from typing import List, Hashable
from fractions import Fraction

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
    @staticmethod
    def create ():
        ctx = Context(
            voice = Voice( "default", instrument = Instrument( 'Acoustic Grand Piano', GeneralMidi.AcousticGrandPiano ) )
        )

        ctx.symbols.assign( ctx.voice.name, ctx.voice )

        return ctx

    def __init__ ( self, 
                   shared : SharedContext = SharedContext(), 
                   voice : Voice = None,
                   cursor : int = 0,
                   symbols : SymbolsScope = SymbolsScope(),
                 ):
        self.shared : SharedContext = shared
        self.voice : Voice = voice
        self.cursor : int = cursor
        self.symbols : SymbolsScope = symbols

    def fork ( self, cursor : int = None, symbols : SymbolsScope = None ) -> 'Context':
        return Context(
            shared = self.shared,
            voice = self.voice,
            cursor = self.cursor if cursor == None else cursor,
            symbols = self.symbols if symbols == None else symbols
        )

    def join ( self, *child_context ):
        for context in child_context:
            if context.cursor > self.cursor:
                self.cursor = context.cursor
    
    def get_value ( self, value : float ) -> float:
        return self.voice.get_value( value )

    def get_duration_ratio ( self ) -> float:
        return self.voice.get_duration_ratio()

    def get_duration ( self, value : float = None ) -> int:
        """Transform a not value into the real world milliseconds it takes, according to the voice's tempo and time signature"""
        return self.voice.get_duration( value )

    def from_duration ( self, milliseconds : int ) -> Fraction:
        """Transform a duration in milliseconds to an approximated note value relative to the tempo and time signature"""
        return self.voice.from_duration( milliseconds )

    def is_linked ( self, library : Library ) -> bool:
        return self.symbols.lookup( library.__class__, container = 'libraries' ) != None

    def link ( self, library : Library ):
        if not self.is_linked( library ):
            library.context = self

            self.symbols.assign( library.__class__, library, container = "libraries" )

            library.on_link()

    def library ( self, library ) -> Library:
        return self.symbols.lookup( library, container = "libraries" )
