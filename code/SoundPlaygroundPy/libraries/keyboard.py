from core import Context, Library, CallableValue

def register_key ( context : Context, key, expression ):
    key_str = key.eval( context )
    
    keys = context.symbols.lookup_internal( "keyboard_keys" )

    keys[ key_str ] = expression

class KeyboardLibrary(Library):
    def on_link ( self, context : Context ):
        context.symbols.assign_internal( "keyboard_keys", dict() )

        context.symbols.assign( "register_key", CallableValue( register_key ) )

    def trigger_key ( key : str, context : Context ):
        keys = context.symbols.lookup_internal( "keyboard_keys" )

        if key in keys:
            return keys[ key ].eval( context )

        return None
