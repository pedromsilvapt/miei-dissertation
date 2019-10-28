from .block_context_modifier_node import BlockContextModifierNode
from core.events import ProgramChangeEvent

class InstrumentBlockModifier( BlockContextModifierNode ):
    def __init__ ( self, body, instrument_name ):
        super().__init__( body )

        self.instrument_name = instrument_name


    def modify ( self, context ):
        instrument = context.symbols.lookup_instrument( self.instrument_name )

        if instrument == None:
            raise BaseException( f"Could not switch to non-existent instrument { self.instrument_name }" )
        
        if instrument.channel == None:
            context.shared.register_instrument( instrument )

            yield ProgramChangeEvent( context.cursor, instrument.channel, instrument.program )

        instrument.ref_count += 1

        context.channel = instrument.channel

    def restore ( self, context ):
        instrument = context.symbols.lookup_instrument( self.instrument_name )

        instrument.ref_count -= 1

        if instrument.ref_count == 0:
            context.shared.unregister_instrument( instrument )
