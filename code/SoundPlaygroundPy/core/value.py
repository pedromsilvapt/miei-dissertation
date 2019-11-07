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

    @property
    def is_truthy ( self ):
        return bool( self.value )

    def __iter__ ( self ):
        return iter( self.value )

class CallableValue(Value):
    def __init__ ( self, value ):
        super().__init__( VALUE_KIND_CALLABLE, value )

    def call ( self, context, args = [], assignment : bool = False ):
        value = self.value( context, *args )

        if isinstance( value, Value ):
            return value
        elif hasattr( value, '__iter__' ):
            if assignment:
                # return Value( VALUE_KIND_MUSIC, SharedMusicEvents( context.fork(), self ) )
                pass
            else:
                return Value( VALUE_KIND_MUSIC, value )
        else:
            return value
