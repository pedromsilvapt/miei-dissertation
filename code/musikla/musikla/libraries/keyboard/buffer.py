from musikla.core.events.transformers.balance_notes import BalanceNotesTransformer
from musikla.core.events.transformers.compose_notes import ComposeNotesTransformer
from musikla.audio.player import PlayerLike
from musikla.audio.interactive_player import InteractivePlayer
from musikla.core.context import Context
from musikla.core.music import Music, MusicBuffer, SharedMusic
from musikla.core.events import MusicEvent
from typing import List, Optional, cast
from .keyboard import Keyboard

class KeyboardBuffer:
    def __init__ ( self, context : Context, keyboards : List[Keyboard] = None, start : bool = True ):
        from .library import KeyboardLibrary
        lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

        self.context = context
        self.keyboards : List[Keyboard] = []
        self.music_buffer : Optional[MusicBuffer] = None
        self.start_time : Optional[int] = None
        self.collected_events : List[MusicEvent] = []
        self.player : PlayerLike = lib.player
        
        if keyboards is None:
            self.keyboards = lib.keyboards
        else:
            self.keyboards = keyboards

        if start: self.start()
    
    @property
    def duration ( self ) -> int:
        if self.collected_events:
            return self.collected_events[ -1 ].end_timestamp
        else:
            return 0

    @property
    def started ( self ) -> bool:
        return self.music_buffer is not None

    def on_new_player ( self, keyboard : Keyboard, player : InteractivePlayer ):
        if self.music_buffer is not None:
            if player.buffers is not None:
                player.buffers.append( self.music_buffer )
            else:
                player.buffers = [ self.music_buffer ]

    def start ( self ):
        if self.music_buffer is None:
            self.start_time = self.player.get_time()
            
            self.music_buffer = MusicBuffer()

            for kb in self.keyboards: kb.add_new_player_observer( self.on_new_player )

    def stop ( self ):
        if self.music_buffer is not None:
            st : int = self.start_time or 0
            
            collected : List[MusicEvent] = [ ev.clone( timestamp = ev.timestamp - st + self.duration ) for ev in self.music_buffer.collect() ]

            self.collected_events.extend( collected )

            self.music_buffer = None

            for kb in self.keyboards: kb.remove_new_player_observer( self.on_new_player )

            self.start_time = None
    
    def clear ( self ):
        self.stop()

        self.collected_events.clear()

    def to_music ( self ):
        return Music( [ *self.collected_events ] ).transform( BalanceNotesTransformer ).transform( ComposeNotesTransformer ).shared()