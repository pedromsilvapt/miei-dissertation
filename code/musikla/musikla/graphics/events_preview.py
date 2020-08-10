import bimpy
from musikla.core.events import MusicEvent, NoteEvent
from musikla.core.events.transformers import DecomposeChordsTransformer
from musikla.core import Voice
from typing import Any, List, Optional, Tuple

class EventsPreview:
    class Viewport:
        def __init__ ( self, width : int, height : int, scroll_vertical : int = 0, scroll_horizontal : int = 0, time_signature = (4, 4), tempo : int = 200, bar_width : int = 60, events_height : float = 2.0 ):
            self.width = width
            self.height = height
            self.time_signature = time_signature
            self.tempo = tempo
            self.bar_width = 200 # bar_width
            self.events_height = events_height
            self.scroll_vertical = scroll_vertical
            self.scroll_horizontal = scroll_horizontal

            ## CACHE
            # Caching these properties allows avoiding recalculating them every
            # frame

            # The cache key is used to know when to invalidate all the calculated values
            self.cache_key = None
            # The voice used to calculate timings inside the viewport
            self.cache_voice : Voice = Voice( "", None, 
                time_signature = self.time_signature,
                tempo = self.tempo
            )
            # How many pixels in width does one second occupy
            self.cache_second_width : int = 0
            # What are the lower and upper pitches that should be visible
            self.cache_fit_pitch_amount : int = 0
            self.cache_lower_pitch : int = 0
            self.cache_upper_pitch : int = 0
            # If the viewport height and event«s height don't subdivide perfectly
            # There can be paddings equally distributed in the top and bottom
            self.cache_vertical_padding : float = 0

        def invalidate_cache ( self ):
            self.cache_key = None

        def validate_cache( self ) -> bool:
            """Checks if the cache is valid. If it is invalid, updates it"""

            key = (self.width, self.height, self.scroll_horizontal, self.scroll_vertical, self.time_signature, self.tempo, self.bar_width, self.events_height)

            if self.cache_key is None or self.cache_key != key:
                self.cache_key = key

                self.cache_voice.time_signature = self.time_signature
                self.cache_voice.tempo = self.tempo

                self.cache_second_width = self.bar_width / ( self.cache_voice.get_bar_duration_absolute() / 1000 )
                
                self.cache_fit_pitch_amount = self.height // self.events_height
                self.cache_vertical_padding = ( self.height % self.events_height ) / 2

                self.cache_lower_pitch = 68 - ( self.cache_fit_pitch_amount // 2 )
                self.cache_upper_pitch = self.cache_lower_pitch + self.cache_fit_pitch_amount

                return False

            return True
        
        def get_pitch_y ( self, pitch : int ) -> Optional[float]:
            if pitch >= self.cache_lower_pitch and pitch <= self.cache_upper_pitch:
                y = self.cache_vertical_padding + ( ( pitch - self.cache_lower_pitch ) * self.events_height )

                return self.height - y

            return None
        
        def get_time_x ( self, time : int, absolute : bool = False ) -> Optional[float]:
            x = ( time * self.cache_second_width / 1000 )

            if absolute:
                return x
            
            x -= self.scroll_horizontal
            
            if x >= 0 and x < self.width:
                return x

            return None

        def scroll_to_time ( self, time : int, anchor : str = 'middle' ):
            time_x = self.get_time_x( time, absolute = True )

            if anchor == 'start':
                self.scroll_horizontal = max( time_x, 0 )
            elif anchor == 'middle':
                self.scroll_horizontal = max( time_x - ( self.width // 2 ), 0 )
            elif anchor == 'end':
                self.scroll_horizontal = max( time_x - self.width, 0 )

    class CachedEvent:
        def __init__ ( self, viewport, event : NoteEvent ):
            self.event : NoteEvent = event

            self.visible : bool = False
            self.start_pos : bimpy.Vec2 = None
            self.end_pos : bimpy.Vec2 = None

            y = viewport.get_pitch_y( int( event ) )

            if y is not None:
                start_x = viewport.get_time_x( event.timestamp )
                end_x = viewport.get_time_x( event.end_timestamp )


                if start_x is not None or end_x is not None:
                    if start_x is None: start_x = 0
                    if end_x is None: end_x = viewport.width

                    self.visible = True

                    self.start_pos = bimpy.Vec2( start_x, y )
                    self.end_pos = bimpy.Vec2( end_x, y )
            

    def __init__ ( self, events : List[MusicEvent], width : int, height : int, viewport = None, margins : Tuple[int, int, int, int] = None ):
        self.events : List[MusicEvent] = events
        # top, right, bottom, left
        self.margins : Tuple[int, int, int, int] = margins or (5, 10, 10, 10)
        self._height : int = height
        self._width : int = width

        self.viewport : EventsPreview.Viewport = viewport or EventsPreview.Viewport( 
            width = width - self.margins_h,
            height = height - self.margins_v,
            bar_width = 60,
            events_height = 2.0
        )

        self.cache_events : Optional[List[EventsPreview.CachedEvent]] = None
        self.cache_rect_start : bimpy.Vec2 = None
        self.cache_rect_end : bimpy.Vec2 = None

    def invalidate_cache ( self ):
        self.cache_events = None

    def validate_cache ( self ) -> bool:
        if self.cache_events is None or not self.viewport.validate_cache():
            self.cache_events = []

            for ev in self.events:
                if isinstance( ev, NoteEvent ):
                    cached_event = EventsPreview.CachedEvent( self.viewport, ev )

                    if cached_event.visible:
                        self.cache_events.append( cached_event )
            
            self.cache_rect_start = bimpy.Vec2( self.margins[ 3 ], self.margins[ 0 ] )
            self.cache_rect_end = bimpy.Vec2( self.width - self.margins[ 1 ], self.height - self.margins[ 2 ] )

            return False
        
        return True

    @property
    def width ( self ) -> int:
        return self._width

    @width.setter
    def width ( self, value ):
        self._width = value
        self.viewport.width = value - self.margins_h

    @property
    def height ( self ) -> int:
        return self._height

    @height.setter
    def height ( self, value ):
        self._height = value
        self.viewport.height = value - self.margins_v

    @property
    def margins_v ( self ) -> int:
        return self.margins[ 0 ] + self.margins[ 2 ]

    @property
    def margins_h ( self ) -> int:
        return self.margins[ 1 ] + self.margins[ 3 ]

    def render ( self ):
        self.validate_cache()
        
        cursor = bimpy.get_cursor_screen_pos()

        rect_start = cursor + self.cache_rect_start
        rect_end = cursor + self.cache_rect_end

        bimpy.add_rect_filled( rect_start, rect_end, 0xFFFFFFFF, 5.0 )

        for ev in self.cache_events:
            if ev.visible:
                bimpy.add_line( rect_start + ev.start_pos, rect_start + ev.end_pos, 0xFF000000, self.viewport.events_height )

        bimpy.set_cursor_pos_y( bimpy.get_cursor_pos_y() + self.height )

class KeyboardBufferPreview:
    def __init__ ( self, buffer, *args, **kargs ):
        from musikla.libraries.keyboard.buffer import KeyboardBuffer

        self.buffer : KeyboardBuffer = buffer
        self.preview : EventsPreview = EventsPreview( [], *args, **kargs )

        self.cache_key = None
        self.cache_events : List[MusicEvent] = []
    
    def invalidate_cache ( self ):
        self.cache_key = None

    def validate_cache ( self ) -> bool:
        len_collected = len( self.buffer.collected_events )
        len_buffered = len( self.buffer.music_buffer.buffer ) \
            if self.buffer.music_buffer is not None else 0

        now_buffer = self.buffer.duration_live

        key = ( len_collected, len_buffered, now_buffer )

        if self.buffer.recording or self.cache_key is None or self.cache_key != key:
            self.cache_key = key

            events = self.buffer.to_events_live( now = True );

            events = DecomposeChordsTransformer.iter( events )

            self.cache_events = list( events )

            self.preview.viewport.scroll_to_time( now_buffer, anchor = 'end' )

            return False
        
        return True

    def render ( self ):
        if not self.validate_cache():
            self.preview.events = self.cache_events
            self.preview.invalidate_cache()
        
        self.preview.render()

        