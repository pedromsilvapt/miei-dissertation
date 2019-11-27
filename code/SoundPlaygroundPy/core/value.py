from typeguard import check_type
from .music import Music

class Value:
    def assignment ( value ):
        # TODO
        if isinstance( value, Music ):
            return value.shared()
        
        return value

    def expect ( value, typehint, name : str = "", soft : bool = False ) -> bool:
        if soft:
            try:
                check_type( name, value, typehint )

                return True
            except:
                return False
        else:
            check_type( name, value, typehint )
            
            return True

    def typeof ( value ):
        return type( value )

    def create ( value ):
        # return value

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
        elif isinstance( value, Music ) or hasattr( value, '__iter__' ):
            return Value( VALUE_KIND_MUSIC, value )
        else:
            return Value( VALUE_KIND_OBJECT, value )

    def eval ( context, node ):
        if node == None: 
            return None

        return node.eval( context )

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

class CallableValue:
    def __init__ ( self, fn ):
        self.fn = fn

    def call ( self, context, args = [], kargs = {} ):
        return self.fn( context, *args, **kargs )

        # if isinstance( value, Value ):
        #     return value
        # elif isinstance( value, Music ):
            # if assignment:
                # FIXME
                # return Value( VALUE_KIND_MUSIC, SharedMusicEvents( context.fork(), self ) )
                # pass
            # else:
                # return value
        # else:
        #     return value

    def __call__ ( self, context, args, kargs ):
        return self.call( context, args, kargs )
