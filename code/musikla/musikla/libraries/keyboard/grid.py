from typing import Any, Optional, Union, cast
from musikla.core import Context, Music
from musikla.core.events import MusicEvent
from musikla.core.events.transformers import SortTransformer
from .keyboard import Keyboard
from fractions import Fraction
import asyncio

DIRECTION_LEFT = 'left'
DIRECTION_RIGHT = 'right'
DIRECTION_BOTH = 'both'

class Grid:
    def __init__ ( self, context : Context, num : int = 1, den : int = 1, forgiveness : int = 0, forgiveness_left : int = 0, forgiveness_right : int = 0, direction : str = DIRECTION_BOTH, sync_with : 'Grid' = None, prealign_with : 'Grid' = None ):
        self.context : Context = context
        self.length : Fraction = Fraction( num, den )
        self.length_duration : int = self.context.voice.get_duration( float( self.length ) )
        
        self._start : Optional[int] = None
        self.realtime : bool = False

        self.range : int = -1
        self.range_left : int = -1
        self.range_right : int = -1

        # A natural number specifying the nonaligment forgiveness: if the event is badly aligned with the grid but the
        # distance is less than the forgiveness set, in milliseconds, then no alignment is performed.
        self.forgiveness : int = forgiveness
        self.forgiveness_left : int = forgiveness_left
        self.forgiveness_right : int = forgiveness_right

        # Determines, when aligning a music event, what direction the alignment can go.
        # Left means that an event is always realigned to the nearest grid elemente befor it
        # Right means that an event is always realigned to the nearest grid element after it
        # Both means that an event is always realigned to the grid element that is closest to it
        self.direction : str = direction

        self.sync_with : Optional['Grid'] = sync_with
        self.prealign_with : Optional['Grid'] = prealign_with

    @property
    def player ( self ):
        from .library import KeyboardLibrary

        library = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        return library.player

    @property
    def start ( self ) -> Optional[int]:
        if self.sync_with is not None:
            return self.sync_with.start

        return self._start

    def get_delta ( self, time : int ) -> int:
        rest = ( time - self.start ) % self.length_duration

        if rest == 0:
            return 0

        delta = 0

        if rest > self.length_duration / 2:
            delta = self.length_duration - rest
        else:
            delta = -rest
        
        fl = self.forgiveness + self.forgiveness_left
        fr = self.forgiveness + self.forgiveness_right

        # if can be forgiven
        if delta > 0 and delta < fl or delta <= 0 and abs( delta ) < fr:
            return 0
        else:
            if self.direction == 'left' and delta > 0:
                return -rest
            elif self.direction == 'right' and delta < 0:
                return self.length_duration - rest
            else:
                return delta

    def reset ( self, base : int = None ):
        if self.sync_with is not None:
            self.sync_with.reset( base )
        else:
            self._start = base

    def _align_event ( self, event : MusicEvent, start_time : int, individually : bool = False, maintain_duration : bool = True ) -> MusicEvent:
        start = self.start

        if start is None:
            self.reset( start_time )

        if individually:
            event_start_delta = self.get_delta( event.timestamp )
        else:
            event_start_delta = self.get_delta( start_time )

        event_end_delta = self.get_delta( event.end_timestamp + event_start_delta ) if not maintain_duration and individually else 0

        return event.clone( 
            timestamp = event_start_delta + event.timestamp, 
            end_timestamp = event_start_delta + event_end_delta + event.end_timestamp 
        )

    def align ( self, context : Context, music : Union[Music, MusicEvent, Any], individually : bool = False, maintain_duration : bool = True ) -> Union[Music, MusicEvent, Any]:
        if self.prealign_with is not None:
            music = self.prealign_with.align( context, music, individually, maintain_duration )

        if isinstance( music, Music ):
            aligned : Music = music.map( lambda e, i, s: self._align_event( e, s, individually, maintain_duration ).join( context ) )

            if individually:
                forgiveness = self.forgiveness + self.forgiveness_left + self.forgiveness_right

                if forgiveness != 0:
                    aligned = aligned.transform( SortTransformer, forgiveness )

            return aligned
        elif isinstance( music, MusicEvent ):
            return self._align_event( music, music.timestamp, individually, maintain_duration )
        else:
            return music

        # if fastforward:
            # aligned = shared = aligned.shared()

            # first_event = shared.peek()

            # if first_event is not None:
            # now = self.player.get_time() - self.start

            # aligned = aligned.slice( start = now, time = True, cut = True )

    @property
    def cell_time ( self ) -> int:
        if self.start is None:
            return 0

        return ( self.player.get_time() - self.start ) % self.length_duration

    def cli_metronome ( self, toolbar_width = 100 ):
        async def periodic():
            while True:
                toolbar_filled = int( self.cell_time * toolbar_width / self.length_duration )
                toolbar_remaining = toolbar_width - toolbar_filled

                print( f'\r[{ "-" * toolbar_filled }{ " " * toolbar_remaining }]    ', end = '' )

                await asyncio.sleep(0.01)

        asyncio.create_task( periodic() )

    @staticmethod
    def compose ( *args ):
        last_grid = args[ 0 ]

        for i in range( 1, len( args ) ):
            args[ i ].sync_with = last_grid.sync_with if last_grid.sync_with is not None else last_grid
            args[ i ].prealign_with = last_grid

            last_grid = args[ i ]

        return last_grid