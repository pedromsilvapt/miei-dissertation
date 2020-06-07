from typing import Any, Optional, Tuple, Union, cast
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
    def __init__ ( self, context : Context, num : int = 1, den : int = 1, forgiveness : int = 0, forgiveness_left : int = 0, forgiveness_right : int = 0, range : int = None, range_left : int = None, range_right : int = None, direction : str = DIRECTION_BOTH, sync_with : 'Grid' = None, prealign_with : 'Grid' = None ):
        self.context : Context = context
        self.length : Fraction = Fraction( num, den )
        self.length_duration : int = self.context.voice.get_duration( float( self.length ) )
        
        self._start : Optional[int] = None
        self.realtime : bool = False

        self.range : Optional[int] = range
        self.range_left : Optional[int] = range_left
        self.range_right : Optional[int] = range_right

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

    def _real_ranges ( self ) -> Tuple[int, int]:
        range = int( self.length_duration / 2 ) if self.range is None else self.range
        
        range_left = range if self.range_left is None else self.range_left
        
        range_right = range if self.range_right is None else self.range_right
        
        if self.range_left is None and self.range_right is not None:
            range_left = range * 2 - self.range_right
        elif self.range_left is not None and self.range_right is None:
            range_right = range * 2 - self.range_left

        return ( range_left, range_right )

    def _real_forgiveness ( self ) -> Tuple[int, int]:
        forgiveness = 0 if self.forgiveness is None else self.forgiveness

        forgiveness_left = forgiveness if self.forgiveness_left is None else self.forgiveness_left
        
        forgiveness_right = forgiveness if self.forgiveness_right is None else self.forgiveness_right
        
        return ( forgiveness_left, forgiveness_right )

    def _within_forgiveness ( self, dist_l : int, dist_r : int ) -> bool:
        fl, fr = self._real_forgiveness()

        return dist_r <= fl or abs( dist_l ) <= fr

    def _within_range ( self, dist_l : int, dist_r : int ) -> int:
        rl, rr = self._real_ranges()

        if dist_l <= rr:
            return dist_r if self.direction == 'right' else -dist_l
        elif dist_r <= rl:
            return -dist_l if self.direction == 'left' else dist_r
        else:
            return 0
    
    def get_delta ( self, time : int ) -> int:
        rest = ( time - self.start ) % self.length_duration

        if rest == 0:
            return 0

        dist_l = rest
        dist_r = self.length_duration - rest
            
        if self._within_forgiveness( dist_l, dist_r ):
            return 0

        return self._within_range( dist_l, dist_r )

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

    def align ( self, context : Context, music : Union[Music, MusicEvent, Any], mode : str = 'start_end', individually : bool = False, maintain_duration : bool = True ) -> Union[Music, MusicEvent, Any]:
        """
        Allowed modes are:
         - global: Changes only the sequence's start time
         - start: Changes the note's start time but retains their duration
         - start_end: Changes both the note's start time and duration to be aligned with the grid
        """

        if self.prealign_with is not None:
            music = self.prealign_with.align( context, music, mode )

        individually = mode != 'global'
        maintain_duration = not individually or mode != 'start_end'

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