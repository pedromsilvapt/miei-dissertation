from py_linq import Enumerable

class SharedContext():
    def __init__ ( self ):
        self.channel_count = 24
        self.channels = dict()

    @property
    def available_channels ( self ):
        return Enumerable.range( 1, self.channel_count )\
            .where( lambda i: i not in self.channels )

    def register_instrument ( self, instrument ):
        channel = self.available_channels\
            .first_or_default()

        if channel == None:
            raise BaseException( "No channel available found" )

        self.channels[ channel ] = instrument

        instrument.channel = channel

    def unregister_instrument ( self, instrument ):
        del self.channels[ instrument.channel ]

        instrument.channel = None
