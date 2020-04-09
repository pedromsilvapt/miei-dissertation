from musikla.core.symbols_scope import SymbolsScope
from typing import Any, Dict, List, Optional
from musikla.core import Context, Music
from musikla.core.theory import Note
from musikla.parser.abstract_syntax_tree import Node
from musikla.audio import Player, AsyncMidiPlayer
from asyncio import Future, sleep, wait, FIRST_COMPLETED, create_task
from fractions import Fraction
from .event import KeyboardEvent

class KeyAction:
    def __init__ ( self, key : KeyboardEvent, expr : Node, args : List[str], context : Context, hold : bool = False, toggle : bool = False, repeat : bool = False, extend : bool = False ):
        self.key : KeyboardEvent = key
        self.expr : Node = expr
        self.args : List[str] = args
        self.context : Context = context
        self.hold : bool = hold
        self.toggle : bool = toggle
        self.repeat : bool = repeat
        self.extend : bool = extend

        self.is_active : bool = False
        self.is_pressed : bool = False

        self.async_player : Optional[AsyncMidiPlayer] = None

    def play ( self, context : Context, player : Player, parameters : Dict[str, Any] ):
        forked_context : Optional[Context] = None

        forked_symbols : SymbolsScope = self.context.symbols.fork( opaque = False )

        for arg in self.args:
            forked_symbols.assign( arg, parameters[ arg ] if arg in parameters else None, local = True )

        def eval ():
            nonlocal forked_context, forked_symbols

            now = player.get_time() if forked_context == None else forked_context.cursor

            forked_context = self.context.fork( cursor = now, symbols = forked_symbols )

            value = self.expr.eval( forked_context )

            if isinstance( value, Music ):
                return value
            elif callable( value ):
                from musikla.core.callable_python_value import CallablePythonValue

                value = CallablePythonValue.call( value, forked_context )

                if isinstance( value, Music ):
                    return value

            return None

        self.async_player = AsyncMidiPlayer( eval, player, 0, self.repeat and not self.extend, self.extend, realtime = True )

        create_task( self.async_player.start() )

    def stop ( self, context : Context, player : Player ):
        if self.async_player != None:
            create_task( self.async_player.stop() )

        self.async_player = None

    def on_press ( self, context : Context, player : Player, parameters : Dict[str, Any] ):
        binary = self.key.binary

        if not binary and self.is_pressed:
            if self.hold or self.toggle:
                return self.on_release( context, player )
            else:
                self.is_pressed = False

        if self.is_pressed:
            return

        self.is_pressed = True
        

        if self.toggle:
            if self.async_player != None and self.async_player.is_playing:
                self.stop( context, player )
            else:
                self.play( context, player, parameters )
        else:
            self.play( context, player, parameters )
        
    def on_release ( self, context : Context, player : Player ):
        if not self.is_pressed:
            return

        self.is_pressed = False

        if self.hold:
            self.stop( context, player )

    def clone ( self, **kargs ) -> 'KeyAction':
        action = KeyAction(
            key = self.key,
            expr = self.expr,
            args = self.args,
            context = self.context,
            toggle = self.toggle,
            hold = self.hold,
            repeat = self.repeat,
            extend = self.extend,
        )

        for key, value in kargs.items():
            setattr( action, key, value )
        
        return action