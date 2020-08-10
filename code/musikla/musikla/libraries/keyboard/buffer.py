from musikla.core.events.transformers.transformer import Transformer
from musikla.core.events.transformers.balance_notes import BalanceNotesTransformer
from musikla.core.events.transformers.compose_notes import ComposeNotesTransformer
from musikla.audio.player import PlayerLike
from musikla.audio.interactive_player import InteractivePlayer
from musikla.core.context import Context
from musikla.core.music import Music, MusicBuffer
from musikla.core.events import MusicEvent
from typing import Dict, List, Optional, cast
from .keyboard import Keyboard

class KeyboardBuffer:
    @staticmethod
    def save_all ( context : Context, file : str, buffers ):
        from musikla.parser.printer import CodePrinter
        from musikla.libraries.music import function_to_mkl
        import musikla.parser.abstract_syntax_tree as ast
        import musikla.parser.abstract_syntax_tree.statements as ast_st
        import musikla.parser.abstract_syntax_tree.expressions as ast_ex

        body = ast_st.StatementsListNode( [] )

        body.statements.append( ast_st.VariableDeclarationStatementNode( 'buffers', ast_ex.ObjectLiteralNode( [] ) ) )

        for key, buffer in buffers.items():
            set_fn = ast_ex.PropertyAccessorNode( ast_ex.VariableExpressionNode( 'buffers' ), ast_ex.StringLiteralNode( 'set' ), True )

            key_p = ast_ex.NumberLiteralNode( key )
            music_p = function_to_mkl( context, buffer.to_music(), ast = True ) \
                if buffer else \
                ast_ex.NoneLiteralNode()

            body.statements.append( ast_ex.FunctionExpressionNode( set_fn, [ key_p, music_p ] ) )

        file_str = CodePrinter().print( body )

        with open( file, 'w+' ) as f:
            f.write( file_str )
    
    @staticmethod
    def load_all ( context : Context, file : str, buffers = None ):
        from musikla.parser.abstract_syntax_tree.expressions.object_literal_node import Object

        buffers = Object() if buffers is None else buffers

        forked_context = context.fork( symbols = context.symbols.fork() )

        context.script.import_module( forked_context, file, save_cache = False )

        saved_buffers = forked_context.symbols.lookup( "buffers", recursive = False )
        
        for key, music in saved_buffers.items():
            bf = buffers.get( key, default = None )

            if bf is None:
                bf = KeyboardBuffer( context, start = False )
            
            if music is not None:
                bf.from_music( music )

            buffers.set( key, bf )
        
        return buffers

    def __init__ ( self, context : Context, keyboards : List[Keyboard] = None, start : bool = True ):
        from .library import KeyboardLibrary
        lib : KeyboardLibrary = cast( KeyboardLibrary, context.library( KeyboardLibrary ) )

        self.context = context
        self.keyboards : List[Keyboard] = []
        self.music_buffer : Optional[MusicBuffer] = None
        self.start_time : Optional[int] = None
        self.collected_events : List[MusicEvent] = []
        self.player : PlayerLike = lib.player
        
        self.loop : bool = False
        self.mode : str = 'music'

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
    def recording ( self ) -> bool:
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

    def stop ( self, discard : bool = False ):
        if self.music_buffer is not None:
            if not discard:

                collected : List[MusicEvent] = list( self.music_buffer.collect() )

                if collected:
                    # We consider the start time as being the first event's timestamp
                    st : int = collected[ 0 ].timestamp

                    collected = [ ev.clone( timestamp = ev.timestamp - st + self.duration ) for ev in collected ]

                    self.collected_events.extend( collected )

            self.music_buffer = None

            for kb in self.keyboards: kb.remove_new_player_observer( self.on_new_player )

            self.start_time = None
    
    def clear ( self ):
        self.stop( discard = True )

        self.collected_events.clear()

    def toggle ( self, clear : bool = True ):
        if self.recording:
            self.stop()
        else:
            if clear: self.clear()

            self.start()

    def __len__ ( self ):
        return len( self.collected_events )

    def __bool__ ( self ):
        return bool( self.collected_events )

    @property
    def duration_live ( self ):
        # Note that this method might return lower values than previous calls
        
        # When we are recording and we have at least on 
        if self.music_buffer is not None and self.music_buffer.buffer:
            st : int = self.music_buffer.buffer[ 0 ].timestamp

            return self.player.get_time() - st + self.duration
        else:
            return self.duration

    def to_events ( self ):
        events = self.collected_events
        events = BalanceNotesTransformer.iter( events )
        events = ComposeNotesTransformer.iter( events )

        return events

    def to_events_live ( self, get_time = None, now : bool = False ):
        if self.music_buffer is not None:
            buffered : List[MusicEvent] = self.music_buffer.buffer

            if buffered:
                # We consider the start time as being the first event's timestamp
                st : int = buffered[ 0 ].timestamp

                buffered = [ ev.clone( timestamp = ev.timestamp - st + self.duration ) for ev in buffered ]

                if now and get_time is None:
                    st : int = buffered[ 0 ].timestamp

                    get_time = lambda: self.duration_live


            events = self.collected_events + buffered
        
            events = BalanceNotesTransformer.iter( events, get_time = get_time )
            events = ComposeNotesTransformer.iter( events )

            return events
        else:
            return self.to_events()

    def to_music ( self ):
        return Music( self.to_events() ).shared()

    def to_music_live ( self ):
        return Music( self.to_events_live() ).shared()

    def from_music ( self, music : Music ):
        self.clear()

        self.collected_events = list( music )