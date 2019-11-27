import fluidsynth
from core.events import MusicEvent, VoiceEvent, NoteEvent, NoteOnEvent, NoteOffEvent, ProgramChangeEvent, ControlChangeEvent, CallbackEvent
from .sequencer import Sequencer
from ctypes import py_object, c_void_p, c_int
from threading import Semaphore
from typing import Dict, Any
from time import sleep

fluid_event_get_data = fluidsynth.cfunc('fluid_event_get_data', c_void_p,
                                    ('evt', c_void_p, 1))

fluid_synth_get_active_voice_count = fluidsynth.cfunc('fluid_synth_get_active_voice_count', c_int,
                                    ('synth', c_void_p, 1))

class FluidSynthSequencer ( Sequencer ):
    def __init__ ( self, output : str = None, soundfont : str = None ):
        super().__init__()

        self.realtime = True

        self.output : str = output or "pulseaudio"
        self.soundfont : str = soundfont or "/usr/share/sounds/sf2/FluidR3_GM.sf2"

        self.synth : fluidsynth.Synth = None
        self.synthId : int = None
        self.soundfontId : int = None
        self.sequencer : fluidsynth.Sequencer = None
        self.client : int = None

        self.last_note : int = None
        self.join_lock : threading.Semaphore = None
        self.start_time : int = 0

        self.events_data : Dict[int, Any] = dict()
        self.events_data_id : int = 1
        self.voices : Dict[str, int] = dict()
    
    def _get_voice_channel ( self, voice ) -> int:
        if voice.name in self.voices:
            return self.voices[ voice.name ]

        self.voices[ voice.name ] = len( self.voices )

        self.synth.program_change( self.voices[ voice.name ], voice.instrument.program )

        return self.voices[ voice.name ]

    @property
    def is_output_file ( self ) -> bool:
        if self.output != None and isinstance( self.output, str ):
            return '.' in self.output
        else:
            return False

    @property
    def playing ( self ):
        if self.synth == None:
            return False

        now = self.get_time()

        return self.last_note != None and now <= self.last_note
        
    def get_time ( self ):
        if self.sequencer == None:
            return 0
        
        return self.sequencer.get_tick() - self.start_time

    def timer ( self, time, data = None, source = -1, dest = -1, absolute = True ):
        if self.last_note == None or self.last_note < time:
            self.last_note = time

        if data != None:
            self.events_data[ self.events_data_id ] = data

            data = c_void_p( self.events_data_id )

            self.events_data_id += 1

        # print( time, data, source, dest, absolute )
        return self.sequencer.timer( time, data = data, source = source, dest = dest, absolute = absolute )

    def apply_event_callback ( self, time, event, seq, data ):
        data = fluid_event_get_data( event )

        if data != None:
            data_id = data

            data = self.events_data[ data_id ]

            del self.events_data[ data_id ]

        if data != None:
            self.apply_event( data )
        else:
            # TODO HACK!!!
            self._join_callback( time, event, seq, data )

    def apply_event ( self, event : MusicEvent ):
        if not event.disabled:
            if isinstance( event, VoiceEvent ):
                channel = self._get_voice_channel( event.voice )
                
                if isinstance( event, NoteOnEvent ):
                     self.synth.noteon( channel, int( event ), event.velocity )
                elif isinstance( event, NoteOffEvent ):
                    self.synth.noteoff( channel, int( event ) )
                elif isinstance( event, ProgramChangeEvent ):
                    self.synth.program_change( channel, event.program )
                elif isinstance( event, ControlChangeEvent ):
                    self.synth.cc( channel, event.control, event.value )
            elif isinstance( event, CallbackEvent ):
                event.call()
            else:
                pass

    def register_event ( self, event : MusicEvent, now = None ):
        if now == None:
            now = self.get_time()
        
        if isinstance( event, VoiceEvent ):
            self._get_voice_channel( event.voice )

        if isinstance( event, NoteEvent ):
            noteon = event.note_on
            noteoff = event.note_off
            
            self.timer( now - self.start_time + noteon.timestamp, data = noteon, dest = self.client )
            self.timer( now - self.start_time + noteoff.timestamp, data = noteoff, dest = self.client )
        else:
            self.timer( now + event.timestamp, data = event, dest = self.client )

    def register_events_many ( self, events, now = None ):
        if now == None:
            now = self.get_time()
        
        for event in events:
            self.register_event( event, now = now )

    def _join_callback ( self, time, event, seq, data ):
        self.join_lock.release()

        self.join_lock = None

    def join ( self ):
        if not self.playing:
            return

        self.join_lock = Semaphore( 0 )

        self.timer( self.last_note + 1000, dest = self.client )
        
        self.join_lock.acquire()

        # while True:
        #     voices = fluid_synth_get_active_voice_count( self.synth.synth )

        #     print( voices )

        #     sleep( 0.3 )

        #     if voices == 0:
        #         break

    def start ( self ):
        self.synth = fluidsynth.Synth()

        # 'alsa', 'oss', 'jack', 'portaudio', 'sndmgr', 'coreaudio', 'Direct Sound', 'pulseaudio'
        fluidsynth.fluid_settings_setint(self.synth.settings, b'audio.period-size', 1024 )
        fluidsynth.fluid_settings_setint( self.synth.settings, b'synth.verbose', 0 )

        if self.is_output_file:
            fluidsynth.fluid_settings_setstr( self.synth.settings, b'audio.file.name', self.output.encode() )
            fluidsynth.fluid_settings_setstr( self.synth.settings, b'audio.driver', 'file'.encode() )
            
            self.synth.audio_driver = fluidsynth.new_fluid_audio_driver( self.synth.settings, self.synth.synth )
        else:
            self.synth.start( driver = self.output )
        
        self.soundfontId = self.synth.sfload( self.soundfont, update_midi_preset = 1 )

        self.synth.cc( 0, 64, 127 )
        self.synth.program_change( 0, 1 )
    
        self.sequencer = fluidsynth.Sequencer()
        
        self.synthId = self.sequencer.register_fluidsynth( self.synth )

        self.client = self.sequencer.register_client( "eventClient", self.apply_event_callback )

        self.start_time = self.sequencer.get_tick()
        
    def close ( self ):
        # TODO Release fluidsynth resources
        pass
