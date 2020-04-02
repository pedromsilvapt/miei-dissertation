from musikla.libraries.keyboard.event import KeyboardEvent
from musikla.core import Context, Library
from musikla.core.theory import Note
from musikla.libraries.midi import MidiLibrary
from musikla.libraries.keyboard import KeyboardLibrary, EventSource, PianoKey
from typing import Any, Dict, Optional, cast
from mido.ports import BaseInput
import asyncio
import mido

class KeyboardMidoLibrary( Library ):
    def __init__ ( self ):
        super().__init__( "keyboard_mido" )

    def on_link ( self, script ):
        keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        if keyboard is not None:
            keyboard.add_source( KeyboardMidoEventSource( self.context ) )

        self.assign( 'MidiEvent', MidiEvent )

class KeyboardMidoEventSource( EventSource ):
    def __init__ ( self, context : Context ):
        self.context : Context = context
        self.midi_port : Optional[BaseInput] = None

    def on_message ( self, virtual_keyboard : KeyboardLibrary, msg : mido.Message ):
        if msg.type == 'note_on':
            note = Note().with_pitch( msg.note )

            virtual_keyboard.on_press( PianoKey( note ) )
        elif msg.type == 'note_off':
            note = Note().with_pitch( msg.note )

            virtual_keyboard.on_release( PianoKey( note ) )
        
        virtual_keyboard.on_press( MidiEvent( msg ) )

    def listen ( self ):
        virtual_keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )
        
        midi = cast( MidiLibrary, self.context.library( MidiLibrary ) )

        if virtual_keyboard is not None and midi is not None:
            loop = asyncio.get_running_loop()

            default_port = midi.get_midi_default_input()

            if default_port is not None:
                self.midi_port = mido.open_input( default_port, callback = lambda msg: loop.call_soon_threadsafe( self.on_message, virtual_keyboard, msg ) )                    
            elif mido.get_input_names():
                self.midi_port = mido.open_input( callback = lambda msg: loop.call_soon_threadsafe( self.on_message, virtual_keyboard, msg ) )

    def close ( self ):
        if self.midi_port is not None:
            self.midi_port.close()

            self.midi_port = None

class MidiEvent( KeyboardEvent ):
    binary : bool = False

    def __init__ ( self, message : mido.Message = None ):
        self.message : mido.Message = message
    
    def get_parameters ( self ) -> Dict[str, Any]:
        return { 'message': self.message }

    def __hash__ ( self ):
        return hash( '<MidiEvent>' )
    
    def __eq__ ( self, other ):
        if other is None:
            return False

        return isinstance( other, MidiEvent )
