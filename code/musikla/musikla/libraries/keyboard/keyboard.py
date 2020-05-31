from decimal import InvalidOperation
from musikla.parser.abstract_syntax_tree.expressions.variable_expression_node import VariableExpressionNode
from musikla.core import Context, Value, Music
from musikla.core.theory import Note
from musikla.core.events import NoteEvent
from typing import Callable, List, Dict, Optional, Union, Any, cast
from musikla.parser.abstract_syntax_tree import Node, MusicSequenceNode
from musikla.parser.abstract_syntax_tree.expressions import BoolLiteralNode, FunctionExpressionNode, ConstantNode, PropertyAccessorNode, StringLiteralNode
from musikla.parser.abstract_syntax_tree.statements import FunctionDeclarationStatementNode
from musikla.audio import Player
from fractions import Fraction
from .event import KeyStroke, PianoKey, KeyboardEvent
from .action import KeyAction

class Keyboard:
    @staticmethod
    def as_event ( key_value : Any ) -> KeyboardEvent:
        if type( key_value ) == str:
            return KeyStroke.parse( key_value )
        elif isinstance( key_value, Music ) or isinstance( key_value, NoteEvent )  or isinstance( key_value, Note ):
            return PianoKey( key_value )
        elif isinstance( key_value, KeyboardEvent ):
            return key_value
        else:
            raise Exception( "Keyboard value is invalid" )

    def __init__ ( self, context : Context ):
        self.context : Context = context        
        self._player : Optional[Player] = None

        self.keys : Dict[KeyboardEvent, KeyAction] = dict()
        self.global_flags : Dict[str, int] = dict()
        self.global_prefixes : List[Node] = list()

        self.manual_lifetime : bool = False

    @property
    def player ( self ) -> Player:
        if self._player is None:
            from .library import KeyboardLibrary

            lib : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

            self._player = lib.player

        return self._player

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

    def __getitem__ ( self, key ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        return self.keys[ key_stroke ]

    def __contains__ ( self, key : Union[ KeyboardEvent, str ] ) -> bool:
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        return key_stroke in self.keys

    def on_press ( self, key : Union[ KeyboardEvent, str ] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_press( self.context, self.player, key_stroke.get_parameters() )

    def on_release ( self, key : Union[str, KeyboardEvent] ):
        key_stroke : KeyboardEvent = cast( KeyboardEvent, KeyStroke.parse( key ) if Value.typeof( key ) == str else key )

        if key_stroke in self.keys:
            self.keys[ key_stroke ].on_release( self.context, self.player )

    def close ( self, closing : bool = False ) -> 'Keyboard':
        from .library import KeyboardLibrary

        self.stop_all()

        if not closing:
            keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

            keyboard.close( self )
        
        return self

    def _assert_keyboard ( self, obj ):
        if obj is None:
            raise InvalidOperation( "Cannot combine a keyboard with 'None'" )
            
        if not isinstance( obj, Keyboard ):
            raise InvalidOperation( f"Cannot combine a keyboard with '{ type( obj ) }'" )

    def clone ( self ):
        from .library import KeyboardLibrary

        lib : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        keyboard = lib.create()
        
        if not self.manual_lifetime:
            self.close()

        keyboard.context = self.context
        keyboard.keys = dict( self.keys )
        keyboard.global_flags = dict( self.global_flags )
        keyboard.global_prefixes = list( self.global_prefixes )
        keyboard.manual_lifetime = self.manual_lifetime
        
        return keyboard

    def map ( self, mapper : Node ) -> 'Keyboard':
        keyboard = self.clone()

        for key, action in self.keys.items():
            keyboard.keys[ key ] = action.clone(
                expr = FunctionExpressionNode( mapper, [ ConstantNode( action.key ), action.expr ] )
            )

        return keyboard

    def with_grid ( self, grid ) -> 'Keyboard':
        body = PropertyAccessorNode( ConstantNode( grid ), StringLiteralNode( 'align' ) )

        body = FunctionExpressionNode( body, [ VariableExpressionNode( 'music' ) ] )

        return self.map( FunctionDeclarationStatementNode( None, [ ( 'k', None, None ), ( 'music', None, None ) ], body ) )

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

        if not other.manual_lifetime:
            other.close()

        self.keys.update( other.keys )

        return self
    
    def __isub__ ( self, other ):
        self._assert_keyboard( other )

        for key in other.keys:
            self.keys.pop( key, None )

        return self

# class ActionMapNode(Node):
#     def __init__ ( self, mapper, key : KeyboardEvent, original : Node ):
#         self.mapper = mapper
#         self.key : KeyboardEvent = key
#         self.original : Node = original
    
#     def eval ( self, context : Context ):
#         result = Value.eval( context, self.original )

        

#         return self.mapper( self.key, result )
