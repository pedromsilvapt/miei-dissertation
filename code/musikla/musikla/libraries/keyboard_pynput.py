from musikla.core import Context, Library
from musikla.libraries.keyboard import KeyboardLibrary, EventSource, MouseMove, MouseClick, MouseScroll, KeyStroke
from pynput.keyboard import Key
from pynput import keyboard, mouse
from typing import Any, List, Optional, Tuple, cast
import asyncio

class KeyboardPynputLibrary( Library ):
    def __init__ ( self ):
        super().__init__( "keyboard_pynput" )

    def on_link ( self, script ):
        keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        if keyboard is not None:
            keyboard.add_source( KeyboardPynputEventSource( self.context ) )

class KeyboardPynputEventSource( EventSource ):
    def __init__ ( self, context : Context ):
        self.context : Context = context
        self.keyboard_listener : Optional[keyboard.Listener] = None
        self.mouse_listener : Optional[mouse.Listener] = None
        self.keyboard_state = dict()

    def get_key_info ( self, key : Key ) -> Tuple[bool, str, int]:
        if hasattr( key, '_value_' ):
            value : int = int( key._value_.vk )
        elif hasattr( key, '_scan' ):
            value : int = key._scan
        else:
            value : int = -1

        key_str = str( key )

        # Hardcoded fix for wrong value for 5 numpad key
        if key_str == '<65437>': key_str = "'5'"

        key_str = key_str[ len( 'Key.' ): ] if key_str.startswith( 'Key.' ) else key_str[ 1:-1 ]

        is_modifier : bool = key_str in [ 'ctrl', 'alt', 'shift' ]
        
        return ( is_modifier, key_str, value )

    def get_keystrokes ( self, is_modifier : bool, key : str, value : int ) -> List[KeyStroke]:
        keystrokes : List[KeyStroke] = []

        ctrl = 'ctrl' in self.keyboard_state
        alt = 'alt' in self.keyboard_state
        shift = 'shift' in self.keyboard_state

        if is_modifier:
            for key in self.keyboard_state.keys():
                if key not in [ 'ctrl', 'alt', 'shift' ]:
                    keystrokes.append( KeyStroke( key, ctrl, alt, shift ) )
                    keystrokes.append( KeyStroke( value, ctrl, alt, shift ) )
        else:
            keystrokes.append( KeyStroke( key, ctrl, alt, shift ) )
            keystrokes.append( KeyStroke( value, ctrl, alt, shift ) )

        return keystrokes

    def on_press ( self, virtual_keyboard : KeyboardLibrary, key : Key ):
        ( is_modifier, key, value ) = self.get_key_info( key )

        self.keyboard_state[ key ] = True
        self.keyboard_state[ value ] = True

        keystrokes = self.get_keystrokes( is_modifier, key, value )
            
        for keystroke in keystrokes:
            if keystroke == KeyStroke( 'c', True, True, True ):
                raise KeyboardInterrupt()
            
            virtual_keyboard.on_press( keystroke )

    def on_release ( self, virtual_keyboard : KeyboardLibrary, key : Key ):
        ( is_modifier, key, value ) = self.get_key_info( key )

        keystrokes = self.get_keystrokes( is_modifier, key, value )

        if key in self.keyboard_state:
            del self.keyboard_state[ key ]

        if value in self.keyboard_state:
            del self.keyboard_state[ value ]

        for keystroke in keystrokes:
            virtual_keyboard.on_release( keystroke )

    def on_move ( self, virtual_keyboard : KeyboardLibrary, x : int, y : int ):
        virtual_keyboard.on_press( MouseMove( x, y ) )

    def on_click ( self, virtual_keyboard : KeyboardLibrary, x : int, y : int, button : int, pressed : bool ):
        virtual_keyboard.on_press( MouseClick( x, y, button, pressed ) )

    def on_scroll ( self, virtual_keyboard : KeyboardLibrary, x : int, y : int, dx : int, dy : int ):
        virtual_keyboard.on_press( MouseScroll( x, y, dx, dy ) )

    def listen ( self ):
        virtual_keyboard : KeyboardLibrary = cast( KeyboardLibrary, self.context.library( KeyboardLibrary ) )

        if virtual_keyboard != None:
            loop = asyncio.get_running_loop()

            self.keyboard_listener = keyboard.Listener(
                on_press = lambda key: loop.call_soon_threadsafe( self.on_press, virtual_keyboard, key ),
                on_release = lambda key: loop.call_soon_threadsafe( self.on_release, virtual_keyboard, key ),
                suppress = False
            )

            self.keyboard_listener.start()

            self.mouse_listener = mouse.Listener(
                on_move = lambda x, y: loop.call_soon_threadsafe( self.on_move, virtual_keyboard, x, y ),
                on_click = lambda x, y, button, pressed: loop.call_soon_threadsafe( self.on_click, virtual_keyboard, x, y, button, pressed ),
                on_scroll = lambda x, y, dx, dy: loop.call_soon_threadsafe( self.on_scroll, virtual_keyboard, x, y, dx, dy )
            )

            self.mouse_listener.start()

    def close ( self ):
        if self.keyboard_listener is not None:
            self.keyboard_listener.stop()

            self.keyboard_listener = None

        if self.mouse_listener is not None:
            self.mouse_listener.stop()

            self.mouse_listener = None

        