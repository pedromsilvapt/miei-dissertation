from musikla.core import Context, Value
from musikla.core.events import NoteEvent
from musikla.core.theory import Note
from typing import List, Dict, Union, Any

class KeyboardEvent:
    binary : bool = True
    
    def get_parameters ( self ) -> Dict[str, Any]:
        return {}

class PianoKey(KeyboardEvent):
    def __init__ ( self, event : Union[NoteEvent, Note] ):
        super().__init__()

        if isinstance( event, NoteEvent ):
            event = event.note

        self.note : Note = event.timeless()
    
    def __eq__ ( self, k ):
        if k is None: return False

        if not isinstance( k, PianoKey ):
            return False

        return self.note == k.note

    def __hash__ ( self ):
        return hash( self.note )

    def __str__ ( self ):
        return str( self.note )

class KeyStroke(KeyboardEvent):
    @staticmethod
    def parse ( s ):
        parts = s.strip().split( "+" )

        key = parts[ -1 ]

        mods = [ s.strip().lower() for s in parts[ :-1 ] ]

        ctrl = 'ctrl' in mods
        alt = 'alt' in mods
        shift = 'shift' in mods

        return KeyStroke( ctrl, alt, shift, key )

    def __init__ ( self, ctrl, alt, shift, key ):
        super().__init__()

        self.ctrl = ctrl
        self.alt = alt
        self.shift = shift
        self.key = key

    def __eq__ ( self, k ):
        if k is None:
            return False

        if not isinstance( k, KeyStroke ):
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

class MouseMove( KeyboardEvent ):
    binary : bool = False

    def __init__ ( self, x : int = 0, y : int = 0 ):
        self.x : int = x
        self.y : int = y
    
    def get_parameters ( self ) -> Dict[str, Any]:
        return { 'x': self.x, 'y': self.y }

    def __hash__ ( self ):
        return hash( '<MouseMove>' )
    
    def __eq__ ( self, other ):
        if other is None:
            return False

        return isinstance( other, MouseMove )

class MouseClick( KeyboardEvent ):
    binary : bool = False

    def __init__ ( self, x : int = 0, y : int = 0, button : int = 0, pressed : bool = False ):
        self.x : int = x
        self.y : int = y
        self.button : int = button
        self.pressed : bool = pressed
    
    def get_parameters ( self ) -> Dict[str, Any]:
        return { 'x': self.x, 'y': self.y, 'button': self.button, 'pressed': self.pressed }

    def __hash__ ( self ):
        return hash( '<MouseClick>' )
    
    def __eq__ ( self, other ):
        if other is None:
            return False

        return isinstance( other, MouseClick )

class MouseScroll( KeyboardEvent ):
    binary : bool = False

    def __init__ ( self, x : int = 0, y : int = 0, dx : int = 0, dy : int = 0 ):
        self.x : int = x
        self.y : int = y
        self.dx : int = dx
        self.dy : int = dy
    
    def get_parameters ( self ) -> Dict[str, Any]:
        return { 'x': self.x, 'y': self.y, 'dx': self.dx, 'dy': self.dy }

    def __hash__ ( self ):
        return hash( '<MouseScroll>' )
    
    def __eq__ ( self, other ):
        if other is None:
            return False

        return isinstance( other, MouseScroll )

class EventSource():
    def listen ( self ):
        pass

    def close ( self ):
        pass