from argparse import ArgumentParser
from musikla.core import Clock, Scheduler
from musikla.core.events import MusicEvent, ControlChangeEvent, ProgramChangeEvent, NoteOnEvent, NoteOffEvent
from musikla.core.events.transformers import DecomposeChordsTransformer, DecomposeNotesTransformer
from .sequencer import Sequencer, SequencerFactory
from typing import Optional
from pathlib import Path
import mido 
import asyncio

class MidiSequencer ( Sequencer ):
    def __init__ ( self, port : str = None, filename : str = None, virtual : bool = False, last_time : int = 0 ):
        super().__init__()

        self.filename : Optional[str] = filename
        self.port : Optional[str] = port
        self.clock : Clock = Clock( auto_start = False )
        self.realtime = self.port is not None
        self.virtual : bool = virtual

        self.scheduler : Scheduler = Scheduler()
        self.port_obj : Optional[mido.ports.BaseOutput] = None
        self.file_obj : Optional[mido.MidiFile] = None
        self.track_obj : Optional[mido.MidiTrack] = None

        self.last_time : int = last_time

        self.set_transformers(
            DecomposeChordsTransformer(),
            DecomposeNotesTransformer()
        )

    @property
    def playing ( self ):
        return True
        
    def get_time ( self ):
        return self.clock.elapsed()

    def _event_to_midi ( self, event : MusicEvent, ticks_per_beat = None ) -> mido.Message:
        if ticks_per_beat is not None:
            t = float( event.timestamp ) / 1000
            lt = float( self.last_time ) / 1000
            delta = mido.second2tick( t, ticks_per_beat ) - mido.second2tick( lt, ticks_per_beat )

            time = delta
        else:
            time = event.timestamp

        self.last_time = event.timestamp

        if isinstance( event, ControlChangeEvent ):
            return mido.Message( 'control_change', channel = 0, control = event.control, value = event.value, time = time )
        elif isinstance( event, ProgramChangeEvent ):
            return mido.Message( 'program_change', channel = 0, program = event.program, time = time )
        elif isinstance( event, NoteOnEvent ):
            return mido.Message( 'note_on', channel = 0, note = int( event ), velocity = event.velocity, time = time )
        elif isinstance( event, NoteOffEvent ):
            return mido.Message( 'note_off', channel = 0, note = int( event ), time = time )

    def send ( self, msg : mido.Message ):
        self.port_obj.send( msg )

    # async def _schedule ( self, delay : float, fn, argument = tuple() ):
    #     await asyncio.sleep( delay )

    #     fn( *argument )

    def schedule ( self, delay : float, fn, argument ):
        asyncio.create_task( self._schedule( delay, fn, argument ) )

    def on_event ( self, event : MusicEvent ):
        if self.track_obj is not None:
            message = self._event_to_midi( event, self.file_obj.ticks_per_beat )

            if message is None:
                return

            self.track_obj.append( message )

        if self.port_obj is not None:
            message = self._event_to_midi( event )

            if message is None:
                return

            # self.schedule( ( message.time - self.clock.elapsed() ) / 1000.0, self.send, argument=( message, ) )
            self.scheduler.enqueue( message.time + self.clock.start_time, self.send, args = ( message, ) )

    def on_close ( self ):
        if self.file_obj is not None:
            self.file_obj.save( self.filename )
        
        if self.port_obj is not None and not self.port_obj.closed:
            self.port_obj.close()

            self.scheduler.stop()

    def join ( self ):
        pass

    def start ( self ):
        if self.filename is not None:
            self.file_obj = mido.MidiFile()

            self.track_obj = self.file_obj.add_track()
        
        if self.port is not None:
            self.port_obj = mido.open_output( self.port, virtual = self.virtual )
            self.scheduler.start()

        self.clock.start()

class MidiSequencerFactory( SequencerFactory ):
    def init ( self ):
        self.name = 'midi'
        self.argparser = ArgumentParser( description = 'Output events to a MIDI file or as MIDI messages to an output port' )
        self.argparser.add_argument( '-p', '--port', dest = 'port', default = False, action='store_true', help = 'Force this output to be treated as a port' )
        self.argparser.add_argument( '-v', '--virtual', dest = 'virtual', default = False, action='store_true', help = 'Whether this is a virtual port to be created' )

    def from_str ( self, uri : str, args ) -> Optional[MidiSequencer]:
        suffix = ( Path( uri ).suffix or '' ).lower()

        is_port = args.port or args.virtual

        if suffix == '.midi' and not is_port:
            return MidiSequencer( filename = uri )
        elif uri.startswith( 'midi://' ):
            return MidiSequencer( port = uri[ len( 'midi://' ): ], virtual = args.virtual )
        elif is_port:
            return MidiSequencer( port = uri, virtual = args.virtual )

