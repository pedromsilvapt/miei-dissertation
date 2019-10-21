import time
import fluidsynth
from py_linq import Enumerable
from core import Note

class MidiCommand():
    def __init__ ( self, timestamp ):
        self.timestamp = timestamp

    def apply ( self, synth ):
        pass

    def sequence ( self, now, sequencer, dest ):
        pass

class ProgramChangeCommand( MidiCommand ):
    def __init__ ( self, timestamp, channel, program ):
        super().__init__( timestamp )

        self.channel = channel
        self.program = program

    def apply ( self, synth ):
        fs.program_change( self.channel, self.program )

    def sequence ( self, now, sequencer, dest ):
        pass
        # raise BaseException( "Program Changes are currently not supported by the sequencer" )

class NoteOnCommand( MidiCommand ):
    def __init__ ( self, timestamp, channel, key, velocity = 127 ):
        super().__init__( timestamp )

        self.channel = channel
        self.key = key
        self.velocity = velocity

    def apply ( self, synth ):
        synth.noteon( self.channel, self.key, self.velocity )

    def sequence ( self, now, sequencer, dest ):
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

    def sequence ( self, now, sequencer, dest ):
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

    def __init__ ( self, events ):
        self.events = events
        self.notes = [ ev for ev in events if isinstance( ev, Note ) ]
        self.commands = MidiPlayer.notes_to_commands( events )
    
    def play ( self ):
        fs = fluidsynth.Synth()

        fluidsynth.fluid_settings_setint(fs.settings, b'audio.period-size', 1024)
        
        fs.start( driver = "pulseaudio" )
        
        sfid = fs.sfload( "/usr/share/sounds/sf2/FluidR3_GM.sf2", update_midi_preset = 1 )

        # TODO Hardcoded Violin Program
        fs.program_change(1, 41)

        fs.cc( 0, 64, 127 )
    
        sequencer = fluidsynth.Sequencer()
        
        synthSeqId = sequencer.register_fluidsynth( fs )

        now = sequencer.get_tick()

        for command in self.commands:
            command.sequence( now, sequencer, synthSeqId )
