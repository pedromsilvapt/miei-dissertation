from typing import Tuple
from .context_modifier_node import ContextModifierNode
from musikla.core.events import ContextChangeEvent
from musikla.core import Context, Voice, Instrument

class InstrumentModifierNode( ContextModifierNode ):
    def __init__ ( self, instrument, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.instrument : int = instrument

    def apply ( self, voice : Voice ):
        voice.instrument = Instrument.from_program( self.instrument )

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( instrument = Instrument.from_program( self.instrument ) )

        yield ContextChangeEvent( context.cursor, "instrument", context.voice.instrument.program )
