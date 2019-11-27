from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context, Voice

class LengthModifierNode( ContextModifierNode ):
    def __init__ ( self, length, position : (int, int) = None ):
        super().__init__( position )

        self.length = length
        
    def apply ( self, voice : Voice ):
        voice.value = self.length

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( value = self.length )

        yield ContextChangeEvent( context.cursor, "length", context.voice.value )
