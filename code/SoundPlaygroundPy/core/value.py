VALUE_KIND_NONE = 0
VALUE_KIND_MUSIC = 1
VALUE_KIND_BOOL = 2
VALUE_KIND_NUMBER = 3
VALUE_KIND_STRING = 4
VALUE_KIND_CALLABLE = 5
VALUE_KIND_OBJECT = 6

class Value:
    def create ( value ):
        if isinstance( value, Value ):
            return Value( value.kind, value.value )

        if value == None:
            return Value( VALUE_KIND_NONE, None )
        elif isinstance( value, bool ):
            return Value( VALUE_KIND_BOOL, value )
        elif isinstance( value, int ) or isinstance( value, float ):
            return Value( VALUE_KIND_NUMBER, value )
        elif isinstance( value, str ):
            return Value( VALUE_KIND_STRING, value )
        elif callable( value ):
            return Value( VALUE_KIND_CALLABLE, value )
        elif hasattr( value, '__iter__' ):
            return Value( VALUE_KIND_MUSIC, value )
        else:
            return Value( VALUE_KIND_OBJECT, value )

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
        if hasattr( self.value, '__iter__' ):
            return iter( self.value )
        
        return iter(())

    def __repr__ ( self ):
        return repr( self.value )

class CallableValue(Value):
    def __init__ ( self, value ):
        super().__init__( VALUE_KIND_CALLABLE, value )

    def call ( self, context, args = [], kargs = {}, assignment : bool = False ):
        value = self.value( context, *args, **kargs )

        if isinstance( value, Value ):
            return value
        elif hasattr( value, '__iter__' ):
            if assignment:
                # FIXME
                # return Value( VALUE_KIND_MUSIC, SharedMusicEvents( context.fork(), self ) )
                pass
            else:
                return Value( VALUE_KIND_MUSIC, value )
        else:
            return value
