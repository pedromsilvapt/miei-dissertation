from musikla.core.events import MusicEvent, VoiceEvent, ContextChangeEvent, NoteEvent, ChordEvent, RestEvent, BarNotationEvent, StaffNotationEvent
from musikla.core.theory import NotePitchClassesInv
from fractions import Fraction
from .file import ABCFile, ABCStaff, ABCVoice, ABCBar, ABCNote, ABCChord, ABCRest, ABCVoiceGroup, ABCVoiceGroupKind
from typing import Dict, Optional
import re

class ABCBuilderConfig:
    def __init__ ( self, visible_voice_names : bool = True, score_merge_voice_staffs : bool = False ):
        self.visible_voice_names : bool = visible_voice_names
        self.score_merge_voice_staffs : bool = score_merge_voice_staffs

class ABCBuilder:
    def __init__ ( self, config : ABCBuilderConfig = None ):
        self.file : ABCFile = ABCFile()

        self.config : ABCBuilderConfig = config or ABCBuilderConfig()

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

    def add_voice_to_score ( self, voice : ABCVoice ):
        match = re.match( r"^(.+?)_[0-9]+$", voice.name_escaped )
        existing_voice : Optional[ABCVoice] = None

        if match is not None:
            existing_voice = next( v for v in self.file.header.voices if v.name_escaped.startswith( match[ 1 ] ) )

        if existing_voice is not None:
            self.file.header.score.groups.append_with( voice.name_escaped, existing_voice.name_escaped )
            
            print( voice.name_escaped, match[ 1 ], existing_voice.name_escaped )
        else:
            group = ABCVoiceGroup( ABCVoiceGroupKind.Parentheses, [ voice.name_escaped ] )

            self.file.header.score.groups.append( group )

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

            if self.config.visible_voice_names:
                voice.label = event.voice.name

            self.file.header.voices.append( voice )
            
            if self.config.score_merge_voice_staffs:
                self.add_voice_to_score( voice )

    def build_note ( self, event : NoteEvent, inside_chord : bool = False ) -> ABCNote:
        note = ABCNote()

        note.accidental = event.accidental
        note.octave = event.octave
        
        if not inside_chord:
            note_length = Fraction( event.value ) / Fraction( self.file.header.length )

            note.length = note_length

        note.pitch_class = NotePitchClassesInv[ event.pitch_class ]
        note.tied = not inside_chord and event.tied

        return note

    def add_note ( self, event : NoteEvent ):
        current_bar = self.get_current_bar( event.voice.name )

        note = self.build_note( event )

        current_bar.symbols.append( note )

    def add_chord ( self, event : ChordEvent ):
        chord_length = Fraction( event.value ) / Fraction( self.file.header.length )

        current_bar = self.get_current_bar( event.voice.name )

        chord = ABCChord()

        chord.notes = [ self.build_note( n, True ) for n in event.notes ]
        chord.length = chord_length
        chord.name = event.name
        chord.tied = event.tied

        current_bar.symbols.append( chord )

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
            elif isinstance( event, ChordEvent ):
                self.add_chord( event )
            elif isinstance( event, RestEvent ):
                self.add_rest( event )
            elif isinstance( event, BarNotationEvent ):
                self.add_bar( event )
            elif isinstance( event, StaffNotationEvent ):
                self.add_staff( event )

    def build ( self ) -> ABCFile:
        return self.file
