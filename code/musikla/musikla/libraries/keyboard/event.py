from musikla.core import Context, Value, Music
from musikla.core.events import NoteEvent
from musikla.core.theory import Note
from typing import List, Dict, Union, Any

class KeyboardEvent:
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'KeyboardEvent':
        raise Exception( "Deserialize not implemented" )

    binary : bool = True
    
    def serialize ( self ) -> str:
        raise Exception( "Serialize not implemented" )

    def get_parameters ( self ) -> Dict[str, Any]:
        return {}

class PianoKey(KeyboardEvent):
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'PianoKey':
        return PianoKey( Note.from_pitch( int( data ) ) )

    def serialize ( self ) -> str:
        return str( int( self.note ) )

    def __init__ ( self, event : Union[Music, NoteEvent, Note, None] ):
        super().__init__()

        if isinstance( event, Music ):
            event = event.first_note( Context() )

        if isinstance( event, NoteEvent ):
            event = event.note

        if event is None:
            raise Exception( "Cannot create PianoKey of None" )

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

class KeyEvent(KeyboardEvent):
    binary : bool = False

    def __init__ ( self, key = None, value = None, pressed : bool = False ):
        super().__init__()

        self.key = key
        self.value = value
        self.pressed = pressed

    def get_parameters ( self ) -> Dict[str, Any]:
        return { 'key': self.key, 'value': self.value, 'pressed': self.pressed }

    def __hash__ ( self ):
        return hash( '<KeyEvent>' )
    
    def __eq__ ( self, other ):
        if other is None:
            return False

        return isinstance( other, KeyEvent )

class KeyStroke(KeyboardEvent):
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'KeyStroke':
        return KeyStroke.parse( data )

    def serialize ( self ) -> str:
        return str( self )

    @classmethod
    def parse ( cls, s ):
        parts = s.strip().split( "+" )

        key = parts[ -1 ]

        mods = [ s.strip().lower() for s in parts[ :-1 ] ]

        ctrl = 'ctrl' in mods
        alt = 'alt' in mods
        shift = 'shift' in mods

        return cls( key, ctrl, alt, shift )

    def __init__ ( self, key, ctrl : bool = False, alt : bool = False, shift : bool = False ):
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

        return '+'.join( [ str(m) for m in mods ] )

class KeyStrokePress( KeyStroke ):
    binary : bool = False

    def __hash__ ( self ):
        return hash( ( "Press ", super().__hash__() ) )

class KeyStrokeRelease( KeyStroke ):
    binary : bool = False
    
    def __hash__ ( self ):
        return hash( ( "Release ", super().__hash__() ) )

class MouseMove( KeyboardEvent ):
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'MouseMove':
        return MouseMove( parameters[ 'x' ], parameters[ 'y' ] )
    
    def serialize ( self ) -> str:
        return ""

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
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'MouseClick':
        return MouseClick(
            parameters[ 'x' ],
            parameters[ 'y' ],
            parameters[ 'button' ],
            parameters[ 'pressed' ]
        )

    def serialize ( self ) -> str:
        return ""

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
    @staticmethod
    def deserialize ( data : str, parameters : Dict[str, Any] ) -> 'MouseScroll':
        return MouseScroll(
            parameters[ 'x' ],
            parameters[ 'y' ],
            parameters[ 'dx' ],
            parameters[ 'dy' ]
        )
    
    def serialize ( self ) -> str:
        return ""

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