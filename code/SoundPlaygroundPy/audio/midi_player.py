import time
import fluidsynth
from py_linq import Enumerable
from core.events import NoteEvent, RestEvent, ProgramChangeEvent

# class MidiCommand():
#     def __init__ ( self, timestamp ):
#         self.timestamp = timestamp

#     def apply ( self, synth ):
#         pass

#     def sequence ( self, now, sequencer, dest, synth ):
#         pass

# class ProgramChangeCommand( MidiCommand ):
#     def __init__ ( self, timestamp, channel, program ):
#         super().__init__( timestamp )

#         self.channel = channel
#         self.program = program

#     def apply ( self, synth ):
#         synth.program_change( self.channel, self.program )

#     def sequence ( self, now, sequencer, dest, synth ):
#         synth.program_change( self.channel, self.program )

#     def __str__ ( self ):
#         return f"<ProgramChange Timestamp={self.timestamp} Channel={self.channel} Program={self.program}>"

# class NoteOnCommand( MidiCommand ):
#     def __init__ ( self, timestamp, channel, key, velocity = 127 ):
#         super().__init__( timestamp )

#         self.channel = channel
#         self.key = key
#         self.velocity = velocity

#     def apply ( self, synth ):
#         synth.noteon( self.channel, self.key, self.velocity )

#     def sequence ( self, now, sequencer, dest, synth ):
#         sequencer.note_on( now + self.timestamp, self.channel, self.key, self.velocity, dest = dest )

#     def __str__ ( self ):
#         return f"<NoteOn Timestamp={self.timestamp} Channel={self.channel} Key={self.key} Velocity={self.velocity}>"
    
# class NoteOffCommand( MidiCommand ):
#     def __init__ ( self, timestamp, channel, key ):
#         super().__init__( timestamp )

#         self.channel = channel
#         self.key = key


#     def apply ( self, synth ):
#         synth.noteoff( self.channel, self.key )

#     def sequence ( self, now, sequencer, dest, synth ):
#         sequencer.note_off( now + self.timestamp, self.channel, self.key, dest = dest )

#     def __str__ ( self ):
#         return f"<NoteOff Timestamp={self.timestamp} Channel={self.channel} Key={self.key}>"

class MidiPlayer():
    # def notes_to_commands ( notes ):
    #     commands = []

    #     for event in notes:
    #         if isinstance( event, NoteEvent ):
    #             key = int( event )

    #             commands.append( NoteOnCommand( event.timestamp, event.channel, key, event.velocity ) )
    #             commands.append( NoteOffCommand( event.timestamp + event.duration, event.channel, key ) )
    #         elif isinstance( event, ProgramChangeEvent ):
    #             commands.append( ProgramChangeCommand( event.timestamp, event.channel, event.program ) )
    #         elif isinstance( event, MidiCommand ):
    #             commands.append( event )
    #         elif isinstance( event, RestEvent ):
    #             pass
    #         else:
    #             raise BaseException( f"Unexpected event: {note}" )

    #     return Enumerable( commands ).order_by( lambda command: command.timestamp ).to_list()

    def __init__ ( self, sequencers = [], events = [] ):
        self.events = events
        self.sequencers = sequencers
        self.started = False
    
    def setup ( self ):
        for seq in self.sequencers:
            seq.start()

    def play ( self ):
        if not self.started:
            self.setup()

            self.started = True

        for seq in self.sequencers:
            seq.register_events_many( self.events )

    def play_more ( self, events ):
        if not self.started:
            self.setup()

            self.started = True

        for seq in self.sequencers:
            seq.register_events_many( events )
            

    def join ( self ):
        if not self.started:
            return

        for seq in self.sequencers:
            seq.join()

