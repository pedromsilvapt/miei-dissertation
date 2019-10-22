from core import Context, Library, CallableValue
from typing import Set

class KeyStroke:
    def parse ( s ):
        parts = s.strip().split( "+" )

        key = parts[ -1 ]

        mods = [ s.strip().lower() for s in parts[ :-1 ] ]

        ctrl = 'ctrl' in mods
        alt = 'alt' in mods
        shift = 'shift' in mods

        return KeyStroke( ctrl, alt, shift, key )

    def __init__ ( self, ctrl, alt, shift, key ):
        self.ctrl = ctrl
        self.alt = alt
        self.shift = shift
        self.key = key

    def __eq__ ( self, k ):
        if k == None:
            return False
        
        return self.ctrl == k.ctrl \
           and self.alt == k.alt \
           and self.shift == k.shift \
           and self.key == k.key

    def __hash__ ( self ):
        return str( self ).__hash__()

    def __str__ ( self ):
        mods = list()

        if self.ctrl: mods.append( 'ctrl' )
        if self.alt: mods.append( 'alt' )
        if self.shift: mods.append( 'shift' )

        mods.append( self.key )

        return '+'.join( mods )


def register_key ( context : Context, key, expression ):
    key_value = key.eval( context )
    
    keys = context.symbols.lookup_internal( "keyboard_keys" )

    keys[ KeyStroke.parse( key_value.value ) ] = expression

class KeyboardLibrary(Library):
    def on_link ( self ):
        context = self.context

        context.symbols.assign_internal( "keyboard_keys", dict() )
        context.symbols.assign_internal( "keyboard_triggered", dict() )

        context.symbols.assign( "register_key", CallableValue( register_key ) )

    def trigger_keys ( self, pressed : KeyStroke ):
        context = self.context

        registered = context.symbols.lookup_internal( "keyboard_keys" )
        triggered = context.symbols.lookup_internal( "keyboard_triggered" )

        for key, expr in registered.items():
            if key in pressed and key not in triggered:
                triggered[ key ] = True

                yield key, expr.eval( context.fork( 0 ) )
            elif key in triggered:
                del triggered[ key ]

    def registered_keys ( self ):    
        return self.context.symbols.lookup_internal( "keyboard_keys" ).items()
