from typing import List, Tuple, Dict
from fractions import Fraction
from musikla.core.theory import NoteAccidental

class ABCVoice:
    def __init__ ( self ):
        self.name : str = None
        self.label : str = None

    def __str__ ( self ):
        if self.label is None:
            return f'V:{ self.name.replace( "/", "_" ) }'
        else:
            return f'V:{ self.name.replace( "/", "_" ) } name="{ self.label }"'

class ABCHeader:
    def __init__ ( self ):
        # X:1
        self.reference : int = 1
        # T:Paddy O'Rafferty
        self.title : str = None
        # C:Trad.
        self.composer : str = None
        # M:6/8
        self.meter : Tuple[int, int] = None
        # L:1/8
        self.length : Fraction = None
        # Q:74
        self.tempo : int = None
        # K:D
        self.key : int = 'C' # Must always be the last field of the header
        # V:V1
        self.voices : List[ABCVoice] = []

    def __str__ ( self ):
        parts : List[str] = []

        if self.reference != None:
            parts.append( f"X:{ self.reference }" )

        if self.title != None:
            parts.append( f"T:{ self.title }" )

        if self.composer != None:
            parts.append( f"C:{ self.composer }" )

        if self.meter != None:
            parts.append( f"M:{ self.meter[ 0 ] }/{ self.meter[ 1 ] }" )
        
        if self.length != None and self.length != 1:
            parts.append( f"L:{ self.length }" )

        if self.tempo != None:
            parts.append( f"Q:{ self.tempo }" )

        for voice in self.voices:
            parts.append( str( voice ) )

        if self.key != None:
            parts.append( f"K:{ self.key }" )

        return '\n'.join( parts )

class ABCSymbol:
    def __init__ ( self ):
        self.length : Fraction = None

class ABCNote(ABCSymbol):
    def __init__ ( self ):
        super().__init__()

        self.pitch_class : str = None
        self.octave : int = None
        self.accidental : int = NoteAccidental.NONE
        self.tied : bool = False

    def __str__ ( self ):
        note : str = self.pitch_class.lower()

        if self.octave <= 3:
            note = note.upper()

            for _ in range( 2, self.octave - 1, -1 ): note += ","
        else:
            for _ in range( 5, self.octave + 1 ): note += "'"
        
        if self.length != None and self.length != 1:
            note += str( self.length )

        if self.tied:
            note += '-'

        if self.accidental == NoteAccidental.DOUBLESHARP:
            note = '^^' + note
        elif self.accidental == NoteAccidental.SHARP:
            note = '^' + note
        elif self.accidental == NoteAccidental.FLAT:
            note = '~' + note
        elif self.accidental == NoteAccidental.DOUBLEFLAT:
            note = '~~' + note

        return note

class ABCChord(ABCSymbol):
    def __init__ ( self ):
        super().__init__()

        self.notes : List[ABCChord] = []
        self.name : str = None
        self.tied : bool = False

    def __str__ ( self ):
        notes = ''.join( str( n ) for n in self.notes )

        chord = f"[{ notes }]"

        if self.name is not None:
            chord = f'"{ self.name }"{ chord }'
        
        if self.length != None and self.length != 1:
            chord += str( self.length )

        if self.tied:
            chord += '-'

        return chord
        

class ABCRest(ABCSymbol):
    def __init__ ( self ):
        self.visible : bool = True

    def __str__ ( self ):
        rest = 'z' if self.visible else 'x'

        if self.length != None and self.length != 1:
            rest += str( self.length )

        return rest

class ABCBar:
    def __init__ ( self ):
        self.symbols : List[ABCSymbol] = []
    
    def __str__ ( self ):
        return ' '.join( [ str( symbol ) for symbol in self.symbols ] )

    @property
    def length ( self ) -> Fraction:
        if len( self.symbols ) == 0:
            return Fraction()
        
        return sum( [ s.length for s in self.symbols if s.length != None ] )

class ABCStaff:
    def __init__ ( self ):
        self.bars : List[ABCBar] = []

    def __str__ ( self ):
        return ' | '.join( [ str( bar ) for bar in self.bars ] ) + ' |'

class ABCBody:
    def __init__ ( self ):
        self.staffs : Dict[str, List[ABCStaff]] = {}

    def __str__ ( self ):
        return '\n'.join( [ f'[V:{voice.replace( "/", "_" )}] ' + str( staff ) for voice, staffs in self.staffs.items() for staff in staffs ] )

# dff cee|def gfe|dff cee|dfe dBA|dff cee|def gfe|faf gfe|1 dfe dBA:|2 dfe dcB|]
# ~A3 B3|gfe fdB|AFA B2c|dfe dcB|~A3 ~B3|efe efg|faf gfe|1 dfe dcB:|2 dfe dBA|]
# fAA eAA|def gfe|fAA eAA|dfe dBA|fAA eAA|def gfe|faf gfe|dfe dBA:|
class ABCFile:
    def __init__ ( self ):
        self.header : ABCHeader = ABCHeader()
        self.body : ABCBody = ABCBody()

    def __str__ ( self ):
        return f"{ self.header }\n{ self.body }\n"
