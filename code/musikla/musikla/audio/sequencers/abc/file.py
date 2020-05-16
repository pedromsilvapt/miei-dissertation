from typing import List, Optional, Tuple, Dict, Union
from fractions import Fraction
from musikla.core.theory import NoteAccidental

class ABCVoice:
    def __init__ ( self ):
        self.name : str = None
        self.label : str = None

    @property
    def name_escaped ( self ) -> str:
        return self.name.replace( "/", "_" )

    def __str__ ( self ):
        if self.label is None:
            return f'V:{ self.name_escaped }'
        else:
            return f'V:{ self.name_escaped } name="{ self.label }"'

class ABCVoiceGroupKind:
    Simple = 0
    Parentheses = 1
    CurlyBraces = 2
    Brackets = 3

class ABCVoiceGroup:
    def __init__ ( self, kind : int = ABCVoiceGroupKind.Simple, members : List[Union[str, 'ABCVoiceGroup']] = [], continuous_staves : bool = False ):
        self.kind : int = kind
        self.members : List[Union[str, ABCVoiceGroup]] = members
        self.continuous_staves : bool = continuous_staves
    
    def __contains__ ( self, voice : str ):
        if voice is not str:
            raise Exception( "ABCVoiceGroup can only contain voices as strings, %s given" % str( type( voice ) ) )

        return any( ( m == voice ) if m is str else ( voice in m ) for m in self.members )

    def append ( self,  voice : Union[str, 'ABCVoiceGroup'] ):
        self.members.append( voice )

    def append_with ( self, voice : Union[str, 'ABCVoiceGroup'], other_voice : str ) -> bool:
        """
        Adds this voice to the same group that also contains `other_voice`.
        Returns true if `other_voice` was found and the `voice` was appended, false otherwise
        """
        for m in self.members:
            if m == other_voice:
                self.append( voice )

                return True
            elif isinstance( m, ABCVoiceGroup ) and m.append_with( voice, other_voice ):
                return True

        return False

    def __str__ ( self ):
        non_empty_members = [ m for m in self.members if m ]

        separator = ' | ' if self.continuous_staves else ' '

        score = separator.join( str( m ) for m in non_empty_members )

        if self.kind == ABCVoiceGroupKind.Parentheses:
            return f"({ score })"
        elif self.kind == ABCVoiceGroupKind.CurlyBraces:
            return f"{{{ score }}}"
        elif self.kind == ABCVoiceGroupKind.Brackets:
            return f"[{ score }]"
        else:
            return score

    def __bool__ ( self ):
        return any( [ bool( m ) for m in self.members ] )

class ABCVoiceScore:
    def __init__ ( self ):
        self.groups : ABCVoiceGroup = ABCVoiceGroup()
        self.verbatim : Optional[str] = None

    def __str__ ( self ):
        has_groups = bool( self.groups )
        has_verbatim = self.verbatim is not None

        if has_groups and has_verbatim:
            return f"{ str( self.groups ) } { self.verbatim }"
        elif has_groups:
            return str( self.groups )
        elif has_verbatim:
            return self.verbatim
        else:
            return ""

    def __bool__ ( self ):
        return bool( self.groups ) or bool( self.verbatim )

class ABCHeader:
    def __init__ ( self ):
        # X:1
        self.reference : int = 1
        # T:Paddy O'Rafferty
        self.title : Optional[str] = None
        # C:Trad.
        self.composer : Optional[str] = None
        # M:6/8
        self.meter : Optional[Tuple[int, int]] = None
        # L:1/8
        self.length : Optional[Fraction] = None
        # Q:74
        self.tempo : Optional[int] = None
        # K:D
        self.key : str = 'C' # Must always be the last field of the header
        # V:V1
        self.voices : List[ABCVoice] = []

        self.score : ABCVoiceScore = ABCVoiceScore()

    def __str__ ( self ):
        parts : List[str] = []

        if self.reference is not None:
            parts.append( f"X:{ self.reference }" )

        if self.title is not None:
            parts.append( f"T:{ self.title }" )

        if self.composer is not None:
            parts.append( f"C:{ self.composer }" )

        if self.meter is not None:
            parts.append( f"M:{ self.meter[ 0 ] }/{ self.meter[ 1 ] }" )
        
        if self.length is not None and self.length != 1:
            parts.append( f"L:{ self.length }" )

        if self.tempo is not None:
            parts.append( f"Q:{ self.tempo }" )

        for voice in self.voices:
            parts.append( str( voice ) )

        if self.score:
            parts.append( f"%%score { str( self.score ) }" )

        if self.key is not None:
            parts.append( f"K:{ self.key }" )

        return '\n'.join( parts )

class ABCSymbol:
    def __init__ ( self ):
        self.length : Optional[Fraction] = None

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
            note = '_' + note
        elif self.accidental == NoteAccidental.DOUBLEFLAT:
            note = '__' + note

        return note

class ABCChord(ABCSymbol):
    def __init__ ( self ):
        super().__init__()

        self.notes : List[ABCNote] = []
        self.name : Optional[str] = None
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
        
        return Fraction( sum( [ s.length for s in self.symbols if s.length != None ] ) )

    def __len__ ( self ):
        return len( self.symbols )

class ABCStaff:
    def __init__ ( self ):
        self.bars : List[ABCBar] = []

    def __str__ ( self ):
        return ' | '.join( [ str( bar ) for bar in self.bars if bar ] ) + ' |'

    def __len__ ( self ):
        return sum( len( b ) for b in self.bars )

class ABCBody:
    def __init__ ( self ):
        self.staffs : Dict[str, List[ABCStaff]] = {}

    def __str__ ( self ):
        return '\n'.join( [ f'[V:{voice.replace( "/", "_" )}] ' + str( staff ) for voice, staffs in self.staffs.items() for staff in staffs if staff ] )

# dff cee|def gfe|dff cee|dfe dBA|dff cee|def gfe|faf gfe|1 dfe dBA:|2 dfe dcB|]
# ~A3 B3|gfe fdB|AFA B2c|dfe dcB|~A3 ~B3|efe efg|faf gfe|1 dfe dcB:|2 dfe dBA|]
# fAA eAA|def gfe|fAA eAA|dfe dBA|fAA eAA|def gfe|faf gfe|dfe dBA:|
class ABCFile:
    def __init__ ( self ):
        self.header : ABCHeader = ABCHeader()
        self.body : ABCBody = ABCBody()

    def __str__ ( self ):
        return f"{ self.header }\n{ self.body }\n"
