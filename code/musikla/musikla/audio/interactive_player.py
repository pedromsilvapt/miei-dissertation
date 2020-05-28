from .player import PlayerLike
from musikla.core.events import NoteOffEvent, ChordOffEvent
from musikla.core.events.transformers import DecomposeNotesTransformer, BalanceNotesTransformer
from typing import Callable, Optional
from musikla.parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, wait, FIRST_COMPLETED

class InteractivePlayer:
    def __init__ ( self, factory : Callable, player : PlayerLike, start_time : int = 0, repeat : bool = False, extend : bool = False, realtime : bool = False ):
        self.factory : Callable = factory
        self.player : PlayerLike = player
        self.repeat : bool = repeat
        self.extend : bool = extend

        # How many milliseconds to try and buffer, minimum
        self.buffer_duration : int = 10

        self.extended_notes = []
        self.events_iterator = None
        self.is_playing : bool = False
        self.realtime : bool = realtime
        self.cancel_token : Optional[CancelToken] = None

    def _generate ( self ):
        pass
        # if self.is_playing:
        #     return

        # self.stop_future = Future()

        # try:
        #     while True:
        #         if self.events_iterator == None:
        #             iterable = self.factory()

        #             if iterable != None and hasattr( iterable, '__iter__' ):
        #                 self.is_playing = True

        #                 self.events_iterator = iter( iterable )
        #             else:
        #                 self.events_iterator = None

        #                 break

        #         if self.is_playing:
        #             events_iterator = self.events_iterator
        #             # First make sure all note events are separated into NoteOn and NoteOff
        #             events_iterator = DecomposeNotesTransformer.iter( events_iterator )
        #             # When extending the notes, ignore any early NoteOn events
        #             if self.extend: 
        #                 events_iterator = filter( lambda ev: not isinstance( ev, NoteOffEvent ) and not isinstance( ev, ChordOffEvent ), events_iterator )

        #             if self.realtime:
        #                 # Then transform the iterator into an async iterator that emits the events only when their timestamp is near
        #                 events_iterator = realtime( events_iterator, self.stop_future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
        #                 # Finally append any missing NoteOff's that might have been cut off because the player stopped playing
        #                 events_iterator = BalanceNotesTransformer.aiter( events_iterator, self.player.get_time )
        #             else:
        #                 events_iterator = BalanceNotesTransformer.iter( events_iterator, self.player.get_time )

        #             yield events_iterator                        
                    
        #             for event in events_iterator:
        #                 if self.extend and ( isinstance( event, NoteOffEvent ) or isinstance( event, ChordOffEvent ) ):
        #                     self.extended_notes.append( event )
        #                 else:
        #                     self.player.play_more( [ event ] )
                    
        #             if self.extend:
        #                 # await
        #                 self.stop_future

        #                 now = self.player.get_time()

        #                 self.player.play_more( [ ev.clone( timestamp = now ) for ev in self.extended_notes ] )

        #             if not self.is_playing or not self.repeat:
        #                 break

        #             self.events_iterator = None
        # finally:
        #     self.is_playing = False

        #     self.stop_future = None

    def start_gen ( self ):
        try:
            for events_iterator in flat_factory( self.factory ):
                self.is_playing = True

                # First make sure all note events are separated into NoteOn and NoteOff
                events_iterator = DecomposeNotesTransformer.iter( events_iterator )
                # When extending the notes, ignore any early NoteOn events
                if self.extend: 
                    events_iterator = filter( lambda ev: not isinstance( ev, NoteOffEvent ) and not isinstance( ev, ChordOffEvent ), events_iterator )
                # Then transform the iterator into an async iterator that emits the events only when their timestamp is near
                # if self.realtime:
                #     events_iterator = realtime( events_iterator, self.stop_future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
                # Finally append any missing NoteOff's that might have been cut off because the player stopped playing
                events_iterator = cancellable( events_iterator, self.cancel_token )

                events_iterator = BalanceNotesTransformer.iter( events_iterator, self.player.get_time )

                for event in events_iterator:
                    if self.extend and ( isinstance( event, NoteOffEvent ) or isinstance( event, ChordOffEvent ) ):
                        self.extended_notes.append( event )
                    else:
                        yield event
                        # self.player.play_more( [ event ] )
                
                # if not self.extend:
                #     self.is_playing = False

                if self.cancel_token.cancelled or not self.repeat:
                    break
        finally:
            if not self.extend:
                self.is_playing = False

                self.cancel_token = None
    
    def stop_gen ( self ):
        if self.cancel_token is not None:
            self.cancel_token.cancel()

    def start_sync ( self ):
        if self.is_playing:
            return

        self.cancel_token = CancelToken()

        self.player.play_more( self.start_gen() )
    
    def stop_sync ( self, now : int ):
        def extended_gen ():
            try:
                for ev in self.extended_notes:
                    yield ev.clone( timestamp = now )
            finally:
                self.is_playing = False
            
        self.stop_gen()
        
        if self.extend:
            self.player.play_more( extended_gen() )
        else:
            self.is_playing = False


    async def start ( self ):
        if self.is_playing:
            return

        self.cancel_token = CancelToken()

        sync_iterator = self.start_gen()

        # if self.cancel_token is None:
        #     return

        if self.realtime:
            iterator = realtime( sync_iterator, self.cancel_token.future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
        else:
            iterator = iter_to_aiter( sync_iterator )
        
        async for event in iterator:
            self.player.play_more( [ event ] )
        
        if self.extend:
            await self.cancel_token.future

            now = self.player.get_time()

            self.player.play_more( [ ev.clone( timestamp = now ) for ev in self.extended_notes ] )

    # async def start ( self ):
    #     if self.is_playing:
    #         return

    #     self.stop_future = Future()

    #     try:
    #         for iterator in flat_factory( self.factory ):
    #             self.is_playing = True

    #             # First make sure all note events are separated into NoteOn and NoteOff
    #             self.events_iterator = DecomposeNotesTransformer.iter( iterator )
    #             # When extending the notes, ignore any early NoteOn events
    #             if self.extend: 
    #                 self.events_iterator = filter( lambda ev: not isinstance( ev, NoteOffEvent ) and not isinstance( ev, ChordOffEvent ), self.events_iterator )
    #             # Then transform the iterator into an async iterator that emits the events only when their timestamp is near
    #             if self.realtime:
    #                 self.events_iterator = realtime( self.events_iterator, self.stop_future, lambda e: e.timestamp, self.player.get_time, self.buffer_duration )
    #             # Finally append any missing NoteOff's that might have been cut off because the player stopped playing
    #             events_iterator = BalanceNotesTransformer.iter( self.events_iterator, self.player.get_time )


    #             async for event in events_iterator:
    #                 if self.extend and ( isinstance( event, NoteOffEvent ) or isinstance( event, ChordOffEvent ) ):
    #                     self.extended_notes.append( event )
    #                 else:
    #                     self.player.play_more( [ event ] )
                
    #             if self.extend:
    #                 await self.stop_future

    #                 now = self.player.get_time()

    #                 self.player.play_more( [ ev.clone( timestamp = now ) for ev in self.extended_notes ] )

    #             if not self.is_playing or not self.repeat:
    #                 break

    #             self.events_iterator = None
    #     finally:
    #         self.is_playing = False

    #         self.stop_future = None

    async def stop ( self ):
        self.stop_gen()
    
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
        
def flat_factory ( factory, count : int = None ):
    i = 0

    while True:
        if count is not None:
            if i >= count:
                break

            i += 1

        iterable = factory()

        if iterable != None and hasattr( iterable, '__iter__' ):
            yield iterable
        else:
            break

class CancelToken():
    def __init__ ( self ):
        self.cancelled = False
        self.future : Future[bool] = Future()
    
    def cancel ( self ):
        if not self.future.done():
            self.cancelled = True
            self.future.set_result( True )

def cancellable ( it, cancel_token : CancelToken ):
    if cancel_token.cancelled:
        return

    for event in it:
        if cancel_token.cancelled:
            break

        yield event

async def iter_to_aiter ( it ):
    for item in it:
        yield item
