from .midi_player import MidiPlayer
from musikla.core.events import MusicEvent, NoteOffEvent
from musikla.core.events.middleware import decompose_notes, balance_notes_async
from typing import List, Callable
from musikla.parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, wait, FIRST_COMPLETED

class AsyncMidiPlayer:
    def __init__ ( self, factory : Callable, player : MidiPlayer, start_time : int = 0, repeat : bool = False, extend : bool = False ):
        self.factory : Callable = factory
        self.player : MidiPlayer = player
        self.repeat : bool = repeat
        self.extend : bool = extend

        # How many milliseconds to try and buffer, minimum
        self.buffer_duration : int = 10

        self.extended_notes = []
        self.events_iterator = None
        self.is_playing : bool = False
        self.stop_future : Future[bool] = None

    async def start ( self ):
        if self.is_playing:
            return

        self.stop_future : Future[bool] = Future()

        try:
            while True:
                if self.events_iterator == None:
                    iterable = self.factory()

                    if iterable != None and hasattr( iterable, '__iter__' ):
                        self.is_playing = True

                        self.events_iterator = iter( iterable )
                    else:
                        break
                        
                if self.is_playing:
                    events_iterator = self.events_iterator
                    # First make sure all note events are separated into NoteOn and NoteOff
                    events_iterator = decompose_notes( events_iterator )
                    # When extending the notes, ignore any early NoteOn events
                    if self.extend: 
                        events_iterator = filter( lambda ev: not isinstance( ev, NoteOffEvent ), events_iterator )
                    # Then transform the iterator into an async iterator that emits the events only when their timestamp is near
                    events_iterator = realtime( events_iterator, self.stop_future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
                    # Finally append any missing NoteOff's that might have been cut off because the player stopped playing
                    events_iterator = balance_notes_async( events_iterator, self.player.get_time )

                    async for event in events_iterator:
                        if self.extend and isinstance( event, NoteOffEvent ):
                            self.extended_notes.append( event )
                        else:
                            self.player.play_more( [ event ], now = 0 )
                    
                    if self.extend:
                        await self.stop_future

                        now = self.player.get_time()

                        self.player.play_more( [ ev.clone( timestamp = now ) for ev in self.extended_notes ], now = 0 )

                    if not self.is_playing or not self.repeat:
                        break

                    self.events_iterator = None
        finally:
            self.is_playing = False

            self.stop_future = None

    async def stop ( self ):
        if self.is_playing and self.stop_future != None:
            self.is_playing = False

            self.stop_future.set_result( True )
    
async def wait_first ( self, *aws ):
    done, _ = await wait( aws, return_when = FIRST_COMPLETED )

    for item in done:
        return item.result()


async def realtime ( source, stop_future, get_timestamp : Callable, get_time : Callable, offset : int ):
    time = get_time()

    for event in source:
        timestamp = get_timestamp( event )

        if timestamp > time - offset:
            stopped = await wait_first( stop_future, sleep( ( timestamp - time - offset ) / 1000, result = False ) )

            if stopped: break

            time = get_time()

        if stop_future.done() and stop_future.result(): break

        yield event
        
async def take_while ( source, predicate : Callable ):
    async for event in source:
        if not predicate(event):
            break
        
        yield event
        