from typeguard import check_type
from .music import Music

class Value:
    @staticmethod
    def assignment ( value ):
        # TODO
        if isinstance( value, Music ):
            return value.shared()
        
        return value

    @staticmethod
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

    @staticmethod
    def typeof ( value ):
        return type( value )

    @staticmethod
    def eval ( context, node ):
        if node == None: 
            return None

        return node.eval( context )

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
