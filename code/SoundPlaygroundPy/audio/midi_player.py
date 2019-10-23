import time
import fluidsynth
from threading import Semaphore
from py_linq import Enumerable
from core import Note

class MidiCommand():
    def __init__ ( self, timestamp ):
        self.timestamp = timestamp

    def apply ( self, synth ):
        pass

    def sequence ( self, now, sequencer, dest, synth ):
        pass

class ProgramChangeCommand( MidiCommand ):
    def __init__ ( self, timestamp, channel, program ):
        super().__init__( timestamp )

        self.channel = channel
        self.program = program

    def apply ( self, synth ):
        synth.program_change( self.channel, self.program )

    def sequence ( self, now, sequencer, dest, synth ):
        synth.program_change( self.channel, self.program )
        # raise BaseException( "Program Changes are currently not supported by the sequencer" )

class NoteOnCommand( MidiCommand ):
    def __init__ ( self, timestamp, channel, key, velocity = 127 ):
        super().__init__( timestamp )

        self.channel = channel
        self.key = key
        self.velocity = velocity

    def apply ( self, synth ):
        synth.noteon( self.channel, self.key, self.velocity )

    def sequence ( self, now, sequencer, dest, synth ):
        # sequencer = fluidsynth.Sequencer()
        # sequencer._schedule_event(  )
        sequencer.note_on( now + self.timestamp, self.channel, self.key, self.velocity, dest = dest )

    def __str__ ( self ):
        return f"<NoteOn Timestamp={self.timestamp} Channel={self.channel} Key={self.key} Velocity={self.velocity}>"
    
class NoteOffCommand( MidiCommand ):
    def __init__ ( self, timestamp, channel, key ):
        super().__init__( timestamp )

        self.channel = channel
        self.key = key


    def apply ( self, synth ):
        synth.noteoff( self.channel, self.key )

    def sequence ( self, now, sequencer, dest, synth ):
        sequencer.note_off( now + self.timestamp, self.channel, self.key, dest = dest )

    def __str__ ( self ):
        return f"<NoteOff Timestamp={self.timestamp} Channel={self.channel} Key={self.key}>"

class MidiPlayer():
    def notes_to_commands ( notes ):
        commands = []

        for note in notes:
            if isinstance( note, Note ):
                key = int( note )

                commands.append( NoteOnCommand( note.timestamp, note.channel, key, note.velocity ) )
                commands.append( NoteOffCommand( note.timestamp + note.duration, note.channel, key ) )
            elif isinstance( note, MidiCommand ):
                commands.append( note )
            else:
                raise BaseException( f"Unexpected event: {note}" )

        return Enumerable( commands ).order_by( lambda command: command.timestamp ).to_list()

    def __init__ ( self, events = [] ):
        self.events = events
        self.notes = [ ev for ev in events if isinstance( ev, Note ) ]
        self.commands = MidiPlayer.notes_to_commands( events )
        self.fs = None
        
        self.latest_command_timestamp = 0
        self.join_client = None
        self.join_client_lock = None
    
    def setup ( self ):
        self.fs = fluidsynth.Synth()

        fluidsynth.fluid_settings_setint(self.fs.settings, b'audio.period-size', 1024)
        
        self.fs.start( driver = "pulseaudio" )
        
        sfid = self.fs.sfload( "/usr/share/sounds/sf2/FluidR3_GM.sf2", update_midi_preset = 1 )

        # self.fs.cc( 0, 64, 127 )
    
        self.sequencer = fluidsynth.Sequencer()
        
        self.synthSeqId = self.sequencer.register_fluidsynth( self.fs )

    def play ( self ):
        if self.fs == None:
            self.setup()

        now = self.sequencer.get_tick()

        for command in self.commands:
            command.sequence( now, self.sequencer, self.synthSeqId, self.fs )

            if command.timestamp + now > self.latest_command_timestamp:
                self.latest_command_timestamp = command.timestamp + now

    def play_more ( self, events ):
        if self.fs == None:
            self.setup()

        now = self.sequencer.get_tick()

        commands = MidiPlayer.notes_to_commands( events )

        for command in commands:
            command.sequence( now, self.sequencer, self.synthSeqId, self.fs )

            if command.timestamp + now > self.latest_command_timestamp:
                self.latest_command_timestamp = command.timestamp + now

    def _joined ( self, time, event, seq, data ):
        self.join_client_lock.release()

        self.join_client_lock = None

    def join ( self ):
        if self.fs == None: return

        now = self.sequencer.get_tick()

        if now >= self.latest_command_timestamp: return

        self.join_client_lock = Semaphore(0)

        self.join_client = self.sequencer.register_client( "join", self._joined )
        
        # Right now we wait until 1 second after the last event
        # In the future we might research a better way
        self.sequencer.timer( self.latest_command_timestamp + 1000, dest = self.join_client )

        self.join_client_lock.acquire()

