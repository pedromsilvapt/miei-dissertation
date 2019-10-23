VALUE_KIND_MUSIC = 1
VALUE_KIND_CALLABLE = 2
VALUE_KIND_STRING = 3
VALUE_KIND_NUMBER = 4

class Value:
    def __init__ ( self, kind, value ):
        self.kind = kind
        self.value = value
    
    @property
    def is_music ( self ):
        return self.kind == VALUE_KIND_MUSIC

    def __iter__ ( self ):
        return iter( self.value )

class CallableValue(Value):
    def __init__ ( self, value ):
        super().__init__( VALUE_KIND_CALLABLE, value )

    def call ( self, context, args ):
        return self.value( context, *args )
