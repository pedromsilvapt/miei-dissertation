VALUE_KIND_MUSIC = 1
VALUE_KIND_CALLABLE = 2
VALUE_KIND_STRING = 3
VALUE_KIND_NUMBER = 4

class Value:
    def __init__ ( self, kind, value ):
        self.kind = kind
        self.value = value
    
    def as_assignment ( self ):
        return self

    def get_events ( self, context ):
        if self.value != None and callable( getattr( self.value, "get_events", None ) ):
            for ev in self.value.get_events( context ):
                yield ev

class CallableValue(Value):
    def __init__ ( self, value ):
        super().__init__( VALUE_KIND_CALLABLE, value )

    def call ( self, context, args ):
        self.value( *args )
