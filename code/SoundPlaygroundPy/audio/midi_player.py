import time
import fluidsynth
from py_linq import Enumerable

class NoteCommand():
    def __init__ ( self, timestamp ):
        self.timestamp = timestamp

    def apply ( self, synth ):
        pass

    def sequence ( self, now, sequencer, dest ):
        pass

class NoteOnCommand( NoteCommand ):
    def __init__ ( self, timestamp, channel, key, velocity = 127 ):
        super().__init__( timestamp )

        self.channel = channel
        self.key = key
        self.velocity = velocity

    def apply ( self, synth ):
        synth.noteon( self.channel, self.key, self.velocity )

    def sequence ( self, now, sequencer, dest ):
        sequencer.note_on( now + self.timestamp, self.channel, self.key, self.velocity, dest = dest )

    def __str__ ( self ):
        return f"<NoteOn Timestamp={self.timestamp} Channel={self.channel} Key={self.key} Velocity={self.velocity}>"
    
class NoteOffCommand( NoteCommand ):
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
            key = int( note )

            commands.append( NoteOnCommand( note.timestamp, note.channel, key, note.velocity ) )
            commands.append( NoteOffCommand( note.timestamp + note.duration, note.channel, key ) )

        return Enumerable( commands ).order_by( lambda command: command.timestamp ).to_list()

    def __init__ ( self, notes ):
        self.notes = notes
        self.commands = MidiPlayer.notes_to_commands( notes )
    
    def play ( self ):
        fs = fluidsynth.Synth()
        
        fs.start( driver = "pulseaudio" )

        sfid = fs.sfload( "/usr/share/sounds/sf2/FluidR3_GM.sf2", update_midi_preset = 1 )
    
        sequencer = fluidsynth.Sequencer()
        
        synthSeqId = sequencer.register_fluidsynth( fs )

        now = sequencer.get_tick()

        for command in self.commands:
            command.sequence( now, sequencer, synthSeqId )
