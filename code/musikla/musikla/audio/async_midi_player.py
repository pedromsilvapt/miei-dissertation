from .player import Player
from musikla.core.events import MusicEvent, NoteOffEvent, ChordOffEvent
from musikla.core.events.transformers import DecomposeNotesTransformer, BalanceNotesTransformer
from typing import List, Callable, Optional
from musikla.parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, wait, FIRST_COMPLETED

class AsyncMidiPlayer:
    def __init__ ( self, factory : Callable, player : Player, start_time : int = 0, repeat : bool = False, extend : bool = False, realtime : bool = False ):
        self.factory : Callable = factory
        self.player : Player = player
        self.repeat : bool = repeat
        self.extend : bool = extend

        # How many milliseconds to try and buffer, minimum
        self.buffer_duration : int = 10

        self.extended_notes = []
        self.events_iterator = None
        self.is_playing : bool = False
        self.stop_future : Optional[Future[bool]] = None
        self.realtime : bool = realtime

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
                    events_iterator = DecomposeNotesTransformer.iter( events_iterator )
                    # When extending the notes, ignore any early NoteOn events
                    if self.extend: 
                        events_iterator = filter( lambda ev: not isinstance( ev, NoteOffEvent ) and not isinstance( ev, ChordOffEvent ), events_iterator )
                    # Then transform the iterator into an async iterator that emits the events only when their timestamp is near
                    if self.realtime:
                        events_iterator = realtime( events_iterator, self.stop_future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
                    # Finally append any missing NoteOff's that might have been cut off because the player stopped playing
                    events_iterator = BalanceNotesTransformer.aiter( events_iterator, self.player.get_time )

                    async for event in events_iterator:
                        if self.extend and ( isinstance( event, NoteOffEvent ) or isinstance( event, ChordOffEvent ) ):
                            self.extended_notes.append( event )
                        else:
                            self.player.play_more( [ event ] )
                    
                    if self.extend:
                        await self.stop_future

                        now = self.player.get_time()

                        self.player.play_more( [ ev.clone( timestamp = now ) for ev in self.extended_notes ] )

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
        