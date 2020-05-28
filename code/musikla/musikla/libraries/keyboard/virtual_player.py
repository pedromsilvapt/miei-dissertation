from musikla.core.enumerable import IterCursor, merge_sorted
from typing import Optional
from musikla.audio.interactive_player import InteractivePlayer
from musikla.core.context import Context
from musikla.core.events.event import MusicEvent
from typing import List, Dict, Tuple, Iterable, Iterator, Generator, TypeVar
from musikla.libraries.keyboard.action import KeyAction
from musikla.core.music import Music
from musikla.libraries.keyboard.keyboard import Keyboard
from musikla.libraries.keyboard.event import KeyboardEvent
from musikla.core.events.transformers import Transformer, ComposeNotesTransformer

T = TypeVar( 'T' )

def concat_iter ( cursor : IterCursor[T], iterable : Iterable[T] ) -> Iterable[T]:
    while not cursor.ended:
        yield cursor.current

        cursor.move_next()
    
    for n in iterable:
        yield n

class VirtualPlayerThread:
    def __init__ ( self, player : InteractivePlayer, iterable : Iterable[MusicEvent] ):
        self.player : InteractivePlayer = player
        self.iterable : Iterable[MusicEvent] = iterable
        self.iterator : Optional[IterCursor[MusicEvent]] = None
        
    def concat ( self, iterable : Iterable[MusicEvent] ):
        if self.iterator is None:
            self.iterator = IterCursor( self.iterable )

            self.iterator.move_next()
        
        self.iterable = concat_iter( self.iterator, iterable )
        self.iterator = None

    def seek ( self, time : int ) -> Iterable[MusicEvent]:
        if self.iterator is None:
            self.iterator = IterCursor( self.iterable )

            self.iterator.move_next()

        while not self.iterator.ended:
            if self.iterator.current is not None:
                if self.iterator.current.timestamp <= time or time < 0:
                    yield self.iterator.current
                else:
                    break

            self.iterator.move_next()

class VirtualPlayer:
    def __init__ ( self ):
        self.queued_interactions : List[Tuple[int, str, KeyboardEvent]] = []
        self._active_actions : Dict[KeyAction, Tuple[KeyAction, Optional[InteractivePlayer]]] = {}
        self._output : List[MusicEvent] = []

        self._transformers : Transformer = ComposeNotesTransformer()
        self._transformers.subscribe( lambda ev: self._output.append( ev ) )

        self._active_key : Optional[KeyAction] = None
        self._active_player : Optional[InteractivePlayer] = None

        self._player_threads : List[VirtualPlayerThread] = []

        self.time : int = 0

    def get_time ( self ) -> int:
        return self.time

    def play_more ( self, events : Iterable[MusicEvent] ):
        if self._active_key is None or self._active_key.interactive_player is None:
            raise Exception( "Trying to play sequence with no key or player attached" )

        if self._active_key.interactive_player == self._active_player:
            for thread in self._player_threads:
                if thread.player == self._active_player:
                    thread.concat( events )
                    break
        else:
            self._player_threads.append( VirtualPlayerThread( self._active_key.interactive_player, events ) )

    def on_press ( self, time : int, key : KeyboardEvent ):
        self.queued_interactions.append( ( time, 'press', key ) )

    def on_release ( self, time : int, key : KeyboardEvent ):
        self.queued_interactions.append( ( time, 'release', key ) )

    def _seek ( self, until : int ):
        iterators = [ thread.seek( until ) for thread in self._player_threads ]

        for ev in merge_sorted( iterators, lambda ev: ev.timestamp ):
            self.time = ev

            self._transformers.add_input( ev )

        if until >= 0:
            self.time = until
    
    def _perform ( self, context : Context, kind : str, key : KeyboardEvent, keyboards : List[Keyboard] ):
        actions : List[KeyAction] = []

        for kb in keyboards:
            if key in kb:
                actions.append( kb[ key ] )
        
        for action in actions:
            virtual_action : KeyAction

            if action in self._active_actions:
                virtual_action, _ = self._active_actions[ action ]
            else:
                virtual_action = action.clone( 
                    sync = True, 
                    is_active = False,
                    is_pressed = False,
                    interactive_player = None 
                )

                self._active_actions[ action ] = ( virtual_action, None )

            self._active_key = virtual_action
            self._active_player = virtual_action.interactive_player

            if kind == 'press':
                virtual_action.on_press( context, self, key.get_parameters() )
            elif kind == 'release':
                virtual_action.on_release( context, self )

            self._active_actions[ action ] = ( virtual_action, virtual_action.interactive_player )

            self._active_key = None
            self._active_player = None
        
    def _generate_music ( self, context : Context, keyboards : List[Keyboard] ):
        # 1. Loop while queue not empty
        for i in range( len( self.queued_interactions ) ):
            # 1.1. Fetch next interaction
            time, kind, key = self.queued_interactions[ i ]

            # 1.3. Seek until next interaction
            self._seek( time )

            # 1.2. Update active actions list
            self._perform( context.fork( cursor = time ), kind, key, keyboards )

        # 2. Seek until the end
        self._seek( -1 )

        # 3. Collect and sort generated events in parallel
        self._transformers.end_input()

        return self._output

    def generate ( self, context : Context, keyboards : List[Keyboard] ) -> Music:
        return Music( self._generate_music( context, keyboards ) )