from musikla.core import symbols_scope
from musikla.core.events.transformers.balance_notes import BalanceNotesTransformer
from musikla.core.events.transformers.compose_notes import ComposeNotesTransformer
from musikla.audio.player import PlayerLike
from musikla.audio.interactive_player import InteractivePlayer
from musikla.core.context import Context
from musikla.core.music import Music, MusicBuffer, SharedMusic
from musikla.core.events import MusicEvent
from typing import Dict, List, Optional, cast
from .keyboard import Keyboard

class KeyboardBuffer:
    @staticmethod
    def save_all ( context : Context, file : str, buffers : Dict[int, 'KeyboardBuffer'] ):
        from musikla.parser.printer import CodePrinter
        from musikla.libraries.music import function_to_mkl
        import musikla.parser.abstract_syntax_tree as ast
        import musikla.parser.abstract_syntax_tree.statements as ast_st
        import musikla.parser.abstract_syntax_tree.expressions as ast_ex

        body = ast_st.StatementsListNode( [] )

        body.statements.append( ast_st.VariableDeclarationStatementNode( 'buffers', ast_ex.ObjectLiteralNode( [] ) ) )

        for key, buffer in buffers.items():
            set_fn = ast_ex.PropertyAccessorNode( ast_ex.VariableExpressionNode( 'buffers' ), ast_ex.StringLiteralNode( 'set' ) )

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

    def __len__ ( self ):
        return len( self.collected_events )

    def __bool__ ( self ):
        return bool( self.collected_events )

    def to_music ( self ):
        return Music( [ *self.collected_events ] ).transform( BalanceNotesTransformer ).transform( ComposeNotesTransformer ).shared()

    def from_music ( self, music : Music ):
        self.collected_events = list( music )