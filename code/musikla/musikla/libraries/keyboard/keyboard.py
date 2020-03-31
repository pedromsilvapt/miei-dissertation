from decimal import InvalidOperation
from musikla.core import Context, Value, Music
from musikla.core.events import NoteEvent
from typing import List, Dict, Optional, Union, Any, cast
from musikla.parser.abstract_syntax_tree import Node, MusicSequenceNode
from musikla.parser.abstract_syntax_tree.expressions import BoolLiteralNode
from musikla.audio import Player
from fractions import Fraction
from .event import KeyStroke, PianoKey, KeyboardEvent
from .action import KeyAction

class Keyboard:
    @staticmethod
    def as_event ( key_value : Any ):
        if type( key_value ) == str:
            return KeyStroke.parse( key_value )
        elif isinstance( key_value, Music ):
            key_event = key_value.first_note()
            
            return PianoKey( key_event )
        elif isinstance( key_value, NoteEvent ):
            return PianoKey( key_value )
        elif isinstance( key_value, KeyboardEvent ):
            return key_value
        else:
            raise Exception( "Keyboard value is invalid" )

    def __init__ ( self, context : Context, player : Player ):
        self.context : Context = context
        self.player : Player = player

        self.keys : Dict[KeyboardEvent, KeyAction] = dict()
        self.global_flags : Dict[str, int] = dict()
        self.global_prefixes : List[Node] = list()

    def get_keyboard_flag ( self, context : Context, node : Optional[Node], name : str ) -> bool:
        if node != None:
            value : Value = node.eval( context )

            return bool( value )

        return name in self.global_flags and self.global_flags[ name ] > 0

    def register_key ( self, context : Context, key : Node, expression : Node, args : List[str] = [], toggle : Node = None, hold : Node = None, repeat : Node = None, extend : Node = None ):
        toggle_value = self.get_keyboard_flag( context, toggle, "toggle" )
        hold_value = self.get_keyboard_flag( context, hold, "hold" )
        repeat_value = self.get_keyboard_flag( context, repeat, "repeat" )
        extend_value = self.get_keyboard_flag( context, extend, "extend" )

        key_value = key.eval( context )

        if self.global_prefixes:
            expression = MusicSequenceNode( [ *self.global_prefixes, expression ] )

        key_event = Keyboard.as_event( key_value )

        action = KeyAction(
            key = key_event,
            expr = expression,
            args = args,
            context = context,
            toggle = toggle_value,
            hold = hold_value,
            repeat = repeat_value,
            extend = extend_value,
        )

        self.keys[ action.key ] = action

    def push_flags ( self, context : Context, *flags : Node ):
        for flag in flags:
            value : str = flag.eval( context )

            if Value.typeof( value ) == str:
                if value in self.global_flags:
                    self.global_flags[ value ] += 1
                else:
                    self.global_flags[ value ] = 1

    def pop_flags ( self, context : Context, *flags : Node ):
        for flag in flags:
            value : str = flag.eval( context )

            if Value.typeof( value ) == str:
                if value in self.global_flags:
                    self.global_flags[ value ] -= 1

                    if self.global_flags[ value ] == 0:
                        del self.global_flags[ value ]

    def push_prefix ( self, context : Context, expression : Node ):
        self.global_prefixes.append( expression )

    def pop_prefix ( self, context : Context ):
        self.global_prefixes.pop()

    def register_key_toggle ( self, context : Context, key : Node, expression : Node ):
        return self.register_key( context, key, expression, toggle = BoolLiteralNode( True ) )

    def register_key_hold ( self, context : Context, key : Node, expression : Node ):
        return self.register_key( context, key, expression, hold = BoolLiteralNode( True ) )

    def start_all ( self ):
        for key in self.keys.values():
            key.play( self.context, self.player, {} )

    def stop_all ( self ):
        for key in self.keys.values():
            key.stop( self.context, self.player )

    def start ( self, key : Union[ KeyboardEvent, str ] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].play( self.context, self.player, key_stroke.get_parameters() )

    def stop ( self, key : Union[ KeyboardEvent, str ] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].stop( self.context, self.player )

    def on_press ( self, key : Union[ KeyboardEvent, str ] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_press( self.context, self.player, key_stroke.get_parameters() )

    def on_release ( self, key : Union[str, KeyboardEvent] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_release( self.context, self.player )

    def close ( self, closing : bool = False ):
        from .library import KeyboardLibrary

        self.stop_all()

        if not closing:
            keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

            keyboard.close( self )

    def _assert_keyboard ( self, obj ):
        if obj is None:
            raise InvalidOperation( "Cannot combine a keyboard with 'None'" )
            
        if not isinstance( obj, Keyboard ):
            raise InvalidOperation( f"Cannot combine a keyboard with '{ type( obj ) }'" )

    def __add__ ( self, other ):
        from .library import KeyboardLibrary

        self._assert_keyboard( other )

        keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        kb = keyboard.create()

        kb += self
        kb += other

        return kb

    def __sub__ ( self, other ):
        from .library import KeyboardLibrary

        self._assert_keyboard( other )

        keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        kb = keyboard.create()

        kb += self
        kb -= other

        return kb

    def __iadd__ ( self, other ):
        self._assert_keyboard( other )

        other.close()

        self.keys.update( other.keys )

        return self
    
    def __isub__ ( self, other ):
        self._assert_keyboard( other )

        for key in other.keys:
            self.keys.pop( key, None )

        return self