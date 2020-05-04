from musikla.core.voice import Voice
from musikla.core.instrument import Instrument
import pyfluidsynth
from musikla.core import Clock
from musikla.core.events import MusicEvent, VoiceEvent, NoteEvent, NoteOnEvent, NoteOffEvent, SoundEvent, ProgramChangeEvent, ControlChangeEvent, CallbackEvent
from musikla.core.events.transformers import DecomposeChordsTransformer
from .sequencer import Sequencer, SequencerFactory, ArgumentParser
from ctypes import c_void_p, c_int
from threading import Semaphore
from typing import Dict, List, Mapping, Tuple, Any, Optional
from time import sleep
from collections import defaultdict
import re

INT_PATTERN = re.compile("^([0-9]+)$")
FLOAT_PATTERN = re.compile("^([0-9]*\.[0-9]+)$")

fluid_synth_get_active_voice_count = pyfluidsynth.cfunc('fluid_synth_get_active_voice_count', c_int,
                                    ('synth', c_void_p, 1))

class FluidSynthSequencer ( Sequencer ):
    def __init__ ( self, output : str = None, soundfont : str = None, settings : Mapping[str, Any] = {} ):
        super().__init__()

        self.realtime = True

        self.output : str = output or "pulseaudio"
        self.soundfont : str = soundfont or "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        self.settings : Mapping[str, Any] = settings

        self.synth : Optional[pyfluidsynth.Synth] = None
        self.synthId : Optional[int] = None
        self.soundfontId : Optional[int] = None
        self.ramSoundfont : Optional[pyfluidsynth.RamSoundFont] = None
        self.ramSoundfontId : Optional[int] = None
        self.sequencer : Optional[pyfluidsynth.Sequencer] = None
        self.client : Optional[int] = None

        self.last_note : Optional[int] = None
        self.join_lock : Optional[Semaphore] = None
        self.start_time : int = 0
        self.keys_count : Dict[int, List[int]] = defaultdict(lambda: [ 0 for i in range( 0, 128 ) ])

        self.events_data : Dict[int, Any] = dict()
        self.events_data_id : int = 1
        self.voices : Dict[str, int] = dict()
        self.samples : Dict[str, Tuple[int, int]] = dict()
        self.samples_voices : Dict[int, Voice] = dict()
        self.last_sample : int = 0
        # For some reason, notes below 15 are somewhat pitched down, and below 10 are heavily pitched down
        # So all samples must start above 15. This means that instead of 128 notes available, we have 113
        self.sample_note_offset : int = 15

        self.clock : Clock = Clock()

        self.set_transformers(
            DecomposeChordsTransformer()
        )
    
    def _get_voice_channel ( self, voice : Voice ) -> int:
        key = voice.name + '$' + str( voice.instrument.program )

        if key in self.voices:
            return self.voices[ key ]

        value = len( self.voices )

        self.voices[ key ] = value

        if voice.instrument.soundfont is None and voice.instrument.bank is None:
            self.synth.program_change( value, voice.instrument.program )
        elif voice.instrument.soundfont is None and voice.instrument.bank is not None:
            self.synth.program_select( value, self.soundfontId, voice.instrument.bank, voice.instrument.program )
        else:
            self.synth.program_select( value, voice.instrument.soundfont, voice.instrument.bank, voice.instrument.program )

        return value

    def _sound_to_note_event ( self, event : SoundEvent ) -> NoteEvent:
        if event.file not in self.samples:
            sno : int = self.sample_note_offset

            sample_location = ( self.last_sample // ( 128 - sno ) + 1, sno + self.last_sample % ( 128 - sno ) )

            self.ramSoundfont.add_wave_zone( 1, sample_location[ 0 ], event.wave, sample_location[ 1 ], sample_location[ 1 ] )
            
            self.samples[ event.file ] = sample_location

            self.last_sample += 1
        else:
            sample_location = self.samples[ event.file ]

        if sample_location[ 0 ] not in self.samples_voices:
            voice = event.voice.clone( name = f"$$sample_voice_{ len( self.samples_voices ) }" )

            voice.instrument = Instrument( f"Samples Virtual Instrument { len( self.samples_voices ) }", sample_location[ 0 ], 1, self.ramSoundfontId )

            self.samples_voices[ sample_location[ 0 ] ] = voice
        else:
            voice = self.samples_voices[ sample_location[ 0 ] ]

        return NoteEvent.from_pitch(
            timestamp = event.timestamp,
            duration = event.duration,
            value = event.value,
            pitch = sample_location[ 1 ],
            velocity = event.velocity,
            voice = voice
        )

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
        data = pyfluidsynth.fluid_event_get_data( event )

        if data != None:
            data_id = data

            data = self.events_data[ data_id ]

            del self.events_data[ data_id ]

        if data != None:
            self.apply_event( data )
        else:
            # TODO HACK!!!
            self._join_callback( time, event, seq, data )

    def apply_event_noteoff ( self, channel, event ):
        key = int( event )

        self.keys_count[ channel ][ key ] -= 1

        if self.keys_count[ channel ][ key ] == 0:
            self.synth.noteoff( channel, key )

    def apply_event_noteon( self, channel, event ):
        key = int( event )

        self.keys_count[ channel ][ key ] += 1

        self.synth.noteon( channel, key, event.velocity )
    
    def apply_event ( self, event : MusicEvent ):
        if isinstance( event, VoiceEvent ):
            channel = self._get_voice_channel( event.voice )
            
            if isinstance( event, NoteOnEvent ):
                self.apply_event_noteon( channel, event )
            elif isinstance( event, NoteOffEvent ):
                self.apply_event_noteoff( channel, event )
            elif isinstance( event, ProgramChangeEvent ):
                self.synth.program_change( channel, event.program )
            elif isinstance( event, ControlChangeEvent ):
                self.synth.cc( channel, event.control, event.value )
        elif isinstance( event, CallbackEvent ):
            event.call()
        else:
            pass

    def on_event ( self, event : MusicEvent ):
        if isinstance( event, VoiceEvent ):
            self._get_voice_channel( event.voice )
        
        if isinstance( event, SoundEvent ):
            event = self._sound_to_note_event( event )
            
        if isinstance( event, NoteEvent ):
            noteon = event.note_on
            noteoff = event.note_off
            
            self.timer( self.start_time + noteon.timestamp, data = noteon, dest = self.client )
            self.timer( self.start_time + noteoff.timestamp, data = noteoff, dest = self.client )    
        else:
            self.timer( event.timestamp, data = event, dest = self.client )
    
    def on_close ( self ):
        # TODO Release fluidsynth resources
        pass

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
        self.synth = pyfluidsynth.Synth()

        # self.synth.setting( 'audio.period-size', 1024 )
        self.synth.setting( 'synth.verbose', 0 )

        for key, value in self.settings.items():
            self.synth.setting( key, value )

        if self.is_output_file:
            self.synth.setting( 'audio.file.name', self.output )
            self.synth.setting( 'audio.driver', 'file' )
            
            self.synth.audio_driver = pyfluidsynth.new_fluid_audio_driver( self.synth.settings, self.synth.synth )
        else:
            self.synth.start( driver = self.output )

        self.soundfontId = self.synth.sfload( self.soundfont, update_midi_preset = 1 )

        self.ramSoundfont = pyfluidsynth.RamSoundFont()
        self.ramSoundfontId = self.synth.add_sfont( self.ramSoundfont )
        
        self.synth.cc( 0, 64, 127 )
        self.synth.program_change( 0, 1 )
    
        self.sequencer = pyfluidsynth.Sequencer()
        
        self.synthId = self.sequencer.register_fluidsynth( self.synth )

        self.client = self.sequencer.register_client( "eventClient", self.apply_event_callback )

        self.start_time = self.sequencer.get_tick()

class FluidSynthSequencerFactory( SequencerFactory ):
    default : bool = True

    def init ( self ):
        self.name = 'fluidsynth'
        self.argparser = ArgumentParser( description = 'Synthesize notes throught the FluidSynthesizer library' )
        self.argparser.add_argument( '-s', '--setting', dest = 'settings', type = str, action='append', help = 'Pass a setting down to fluidsynth with the format <key>=<value>' )
        self.argparser.add_argument( '-c', '--audio-bufcount', dest = 'audio_buffcount', type = int, action='store', help = 'Number of audio buffers (equivalent to `audio.periods`)' )
        self.argparser.add_argument( '-g', '--gain', dest = 'gain', type = float, action='store', help = 'Set the master gain [0 < gain < 10, default = 0.2] (equivalent to `synth.gain`)' )
        self.argparser.add_argument( '-K', '--midi-channels', dest = 'midi_channels', type = int, action='store', help = 'The number of midi channels [default = 16] (equivalent to `synth.midi-channels`)' )
        self.argparser.add_argument( '-L', '--audio-channels', dest = 'audio_channels', type = int, action='store', help = 'The number of stereo audio channels [default = 1] (equivalent to `synth.audio-channels`)' )
        self.argparser.add_argument( '-r', '--sample-rate', dest = 'sample_rate', type = float, action='store', help = 'Set the sample rate (equivalent to `synth.sample-rate`)' )
        self.argparser.add_argument( '-z', '--audio-buffsize', dest = 'audio_buffsize', type = float, action='store', help = 'Size of each audio buffer (equivalent to `audio.period-size`)' )

    def _args_settings_dictionary ( self, args ):
        settings_dict = {}

        for arg in args.settings or []:
            if '=' not in arg:
                settings_dict[ arg ] = True
            else:
                key, value = arg.split( '=' )

                if value == 'true':
                    settings_dict[ arg ] = True
                elif value == 'false':
                    settings_dict[ arg ] = False
                elif FLOAT_PATTERN.match( value ):
                    settings_dict[ arg ] = float( value )
                elif INT_PATTERN.match( value ):
                    settings_dict[ arg ] = int( value )
                else:
                    settings_dict[ arg ] = value

        if args.audio_buffcount is not None:
            settings_dict[ 'audio.periods' ] = args.audio_buffcount
        if args.gain is not None:
            settings_dict[ 'synth.gain' ] = args.gain
        if args.midi_channels is not None:
            settings_dict[ 'synth.midi-channels' ] = args.midi_channels
        if args.audio_channels is not None:
            settings_dict[ 'synth.audio-channels' ] = args.audio_channels
        if args.sample_rate is not None:
            settings_dict[ 'synth.sample-rate' ] = args.sample_rate
        if args.audio_buffsize is not None:
            settings_dict[ 'audio.period-size' ] = args.audio_buffsize

        return settings_dict

    def from_str ( self, uri : str, args ) -> FluidSynthSequencer:
        soundfont = self.config.get( 'Musikla', 'soundfont', fallback = None )

        cli_settings = self._args_settings_dictionary( args )
        ini_settings = self.config[ 'FluidSynth.Settings' ] if 'FluidSynth.Settings' in self.config else {}

        return FluidSynthSequencer( uri, soundfont, { **cli_settings, **ini_settings } )
