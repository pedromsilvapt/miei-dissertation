from core.events import MusicEvent, ContextChangeEvent, NoteEvent, RestEvent
from core.theory import NotePitchClassesInv
from fractions import Fraction
from .file import ABCFile, ABCStaff, ABCBar, ABCNote, ABCRest
from typing import Dict

class ABCBuilder:
    def __init__ ( self ):
        self.file : ABCFile = ABCFile()

    @property
    def staff_capacity ( self ) -> int:
        sig : int = self.file.header.meter[ 1 ]

        if sig == 2: return 8
        elif sig == 3: return 6
        elif sig == 4: return 4
        elif sig == 8: return 2

    @property
    def bar_capacity ( self ) -> Fraction:
        return Fraction( self.file.header.meter[ 0 ], self.file.header.meter[ 1 ] )

    def get_current_staff ( self, create_if_full : bool = True ) -> ABCStaff:
        if len( self.file.body.staffs ) == 0:
            staff = ABCStaff()

            self.file.body.staffs.append( staff )
        else:
            if create_if_full and len( self.file.body.staffs ) == self.staff_capacity:
                self.file.body.staffs.append( ABCStaff() )
            
            staff = self.file.body.staffs[ -1 ]

        return staff

    def get_current_bar ( self, create_if_full : bool = True ) -> ABCBar:
        staff = self.get_current_staff( create_if_full = False )

        if len( staff.bars ) == 0:
            bar = ABCBar()

            staff.bars.append( bar )
        else:
            bar = staff.bars[ -1 ]

        if create_if_full and bar.length * self.file.header.length >= self.bar_capacity:
            staff = self.get_current_staff( create_if_full = True )

            bar = ABCBar()

            staff.bars.append( bar )

        return bar

    def add_context_change ( self, event : ContextChangeEvent ):
        if event.property == 'length':
            self.file.header.length = Fraction( event.value )
        elif event.property == 'timeSignature':
            self.file.header.meter = event.value
        elif event.property == 'tempo':
            self.file.header.tempo = event.value


    # def get_duration_ratio ( self ) -> float:
    #     ( u, l ) = self.time_signature

    #     if u >= 6 and u % 3 == 0:
    #         return 3 / l
    #     else:
    #         return 1 / l

    # def get_duration ( self, value : float = None ) -> int:
    #     beat_duration = 60 / self.tempo

    #     whole_note_duration = beat_duration * 1000.0 / self.get_duration_ratio()

    #     return int( whole_note_duration * self.get_value( value ) )


    def add_note ( self, event : NoteEvent ):
        # TODO Header length might be None
        note_length = Fraction( event.value ) / self.file.header.length

        current_bar = self.get_current_bar( create_if_full = True )

        note = ABCNote()

        note.accidental = event.accidental
        note.octave = event.octave
        note.length = note_length
        note.pitch_class = NotePitchClassesInv[ event.pitch_class ]

        current_bar.symbols.append( note )


    def add_rest ( self, event : RestEvent ):
        rest_length = Fraction( event.value ) / self.file.header.length

        current_bar = self.get_current_bar( create_if_full = True )

        rest = ABCRest()

        rest.length = rest_length
        rest.visible = event.visible

        current_bar.symbols.append( rest )

    def add_event ( self, event : MusicEvent ):
        if isinstance( event, ContextChangeEvent ):
            self.add_context_change( event )
        elif isinstance( event, NoteEvent ):
            self.add_note( event )
        elif isinstance( event, RestEvent ):
            self.add_rest( event )

    def build ( self ) -> ABCFile:
        return self.file
