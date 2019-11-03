from .midi_player import MidiPlayer
from core import Context
from core.events import MusicEvent
from typing import List, Callable
from parser.abstract_syntax_tree import Node
from asyncio import Future, sleep, wait, FIRST_COMPLETED

class AsyncMidiPlayer:
    def __init__ ( self, factory : Callable, player : MidiPlayer, start_time : int = 0, repeat : bool = False ):
        self.factory : Callable = factory
        self.player : MidiPlayer = player
        self.repeat : bool = repeat
        self.start_time = start_time

        # How many milliseconds to try and buffer, minimum
        self.buffer_duration : int = 250

        self.buffer = None
        self.events_iterator = None
        self.is_playing : bool = False
        self.stop_future : Future[bool] = None
        self.forked_context : Context = None

    async def wait_first ( self, *aws ):
        done, pending = await wait( aws, return_when = FIRST_COMPLETED )

        for item in done:
            return item.result()

    def fill_buffer ( self, iterator, now : int ) -> List[MusicEvent]:
        buffer : List[MusicEvent] = []
        
        try:
            while True:
                event : MusicEvent = next( iterator )

                buffer.append( event )

                if event.timestamp >= now + self.buffer_duration:
                    break
        except StopIteration:
            if len( buffer ) == 0:
                return None

        return buffer

    async def start ( self ):
        if self.is_playing:
            return

        self.stop_future : Future[bool] = Future()

        try:
            while True:
                if self.events_iterator == None:
                    iterable = self.factory()

                    if iterable != None:
                        self.is_playing = True

                        self.events_iterator = iter( iterable )
                    else:
                        break
                        
                if self.is_playing:
                    now = self.player.get_time()

                    self.buffer = self.fill_buffer( self.events_iterator, now )

                    if self.buffer == None:
                        self.events_iterator = None

                        if self.repeat:
                            continue
                        else:
                            break

                    self.player.play_more( self.buffer, now = 0 )

                    last_event = self.buffer[ -1 ]

                    stopped = await self.wait_first( self.stop_future, sleep( ( last_event.timestamp - now - 50 ) / 1000, result = False ) )

                    if stopped == True:
                        now = self.player.get_time()

                        for event in self.buffer:
                            if event.timestamp > now:
                                event.disabled = True
        finally:
            self.is_playing = False

            self.stop_future = None

    async def stop ( self ):
        if self.is_playing and self.stop_future != None:
            self.stop_future.set_result( True )
        