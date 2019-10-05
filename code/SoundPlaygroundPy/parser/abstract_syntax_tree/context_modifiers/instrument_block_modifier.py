from .block_context_modifier_node import BlockContextModifierNode

class InstrumentBlockModifier( BlockContextModifierNode ):
    def __init__ ( self, body, instrument_name ):
        super().__init__( body )

        self.instrument_name = instrument_name


    def modify ( self, context ):
        if self.instrument_name not in context.instruments:
            raise BaseException( f"Could not switch to non-existent instrument { self.instrument_name }" )
            
        instrument = context.instruments[ self.instrument_name ]

        if instrument.channel == None:
            context.shared.register_instrument( instrument )

        instrument.ref_count += 1

        context.channel = instrument.channel

    def restore ( self, context ):
        instrument = context.instruments[ self.instrument_name ]

        instrument.ref_count -= 1

        if instrument.ref_count == 0:
            context.shared.unregister_instrument( instrument )
