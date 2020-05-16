from typing import Tuple
from .context_modifier_node import ContextModifierNode
from musikla.core.events import ContextChangeEvent
from musikla.core import Context, Voice

class LengthModifierNode( ContextModifierNode ):
    def __init__ ( self, length, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.length = length
        
    def apply ( self, voice : Voice ):
        voice.value = self.length

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( value = self.length )

        yield ContextChangeEvent( context.cursor, "length", context.voice.value, context.voice, 0 )
