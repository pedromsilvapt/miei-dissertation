from core import Context

def register_key ( context : Context, key, expression ):
    key_str = ...

    keys = context.symbols.lookup_internal( "keyboard_keys" )

    keys[ key ] = expression
    
def Library:
    def on_link ( self, context : Context ):
        pass

def KeyboardLibrary(Library):
    def on_link ( self, context : Context ):
        context.symbols.assign_internal( "keyboard_keys", dict() )

        context.symbols.assign( "register_key", CallableValue( register_key ) )
