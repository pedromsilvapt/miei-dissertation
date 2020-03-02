from musikla.core.events import MusicEvent, VoiceEvent, ContextChangeEvent, NoteEvent, RestEvent, BarNotationEvent, StaffNotationEvent
from musikla.core.theory import NotePitchClassesInv
from fractions import Fraction
from .file import ABCFile, ABCStaff, ABCVoice, ABCBar, ABCNote, ABCRest
from typing import Dict

class ABCBuilder:
    def __init__ ( self ):
        self.file : ABCFile = ABCFile()

    def get_current_staff ( self, voice : str ) -> ABCStaff:
        if voice not in self.file.body.staffs:
            self.file.body.staffs[ voice ] = []
        
        if len( self.file.body.staffs[ voice ] ) == 0:
            staff = ABCStaff()

            self.file.body.staffs[ voice ].append( staff )
        else:
            staff = self.file.body.staffs[ voice ][ -1 ]

        return staff

    def get_current_bar ( self, voice : str ) -> ABCBar:
        staff = self.get_current_staff( voice )

        if len( staff.bars ) == 0:
            bar = ABCBar()

            staff.bars.append( bar )
        else:
            bar = staff.bars[ -1 ]

        return bar

    def add_context_change ( self, event : ContextChangeEvent ):
        if event.property == 'length':
            self.file.header.length = Fraction( event.value )
        elif event.property == 'timeSignature':
            self.file.header.meter = event.value
        elif event.property == 'tempo':
            self.file.header.tempo = event.value

    def add_voice ( self, event : VoiceEvent ):
        if self.file.header.length is None:
            self.file.header.length = Fraction( event.voice.value )
        
        if self.file.header.meter is None:
            self.file.header.meter = event.voice.time_signature

        if self.file.header.tempo is None:
            self.file.header.tempo = event.voice.tempo

        if event.voice.name not in self.file.body.staffs:
            self.file.body.staffs[ event.voice.name ] = []

            voice = ABCVoice()
            voice.name = event.voice.name
            voice.label = event.voice.name

            self.file.header.voices.append( voice )

    def add_note ( self, event : NoteEvent ):
        note_length = Fraction( event.value ) / Fraction( self.file.header.length )

        current_bar = self.get_current_bar( event.voice.name )

        note = ABCNote()

        note.accidental = event.accidental
        note.octave = event.octave
        note.length = note_length
        note.pitch_class = NotePitchClassesInv[ event.pitch_class ]
        note.tied = event.tied

        current_bar.symbols.append( note )

    def add_rest ( self, event : RestEvent ):
        rest_length = Fraction( event.value ) / Fraction( self.file.header.length )

        current_bar = self.get_current_bar( event.voice.name )

        rest = ABCRest()

        rest.length = rest_length
        rest.visible = event.visible

        current_bar.symbols.append( rest )

    def add_bar ( self, event : BarNotationEvent ):
        staff = self.get_current_staff( event.voice.name )

        staff.bars.append( ABCBar() )

    def add_staff ( self, event : StaffNotationEvent ):
        name = event.voice.name
        if name not in self.file.body.staffs:
            self.file.body.staffs[ name ] = [ ABCStaff() ]
        else:
            self.file.body.staffs[ name ].append( ABCStaff() )

    def add_event ( self, event : MusicEvent ):
        if isinstance( event, ContextChangeEvent ):
            self.add_context_change( event )
        else:
            if isinstance( event, VoiceEvent ):
                self.add_voice( event )

            if isinstance( event, NoteEvent ):
                self.add_note( event )
            elif isinstance( event, RestEvent ):
                self.add_rest( event )
            elif isinstance( event, BarNotationEvent ):
                self.add_bar( event )
            elif isinstance( event, StaffNotationEvent ):
                self.add_staff( event )

    def build ( self ) -> ABCFile:
        return self.file
