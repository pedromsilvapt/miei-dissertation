from .context_modifier_node import ContextModifierNode
from core.events import ContextChangeEvent
from core import Context, Voice

class OctaveModifierNode( ContextModifierNode ):
    def __init__ ( self, octave, position : (int, int) = None ):
        super().__init__( position )

        self.octave = octave
        
    def apply ( self, voice : Voice ):
        voice.octave = self.octave

    def modify ( self, context : Context ):
        context.voice = context.voice.clone( octave = self.octave )

        yield ContextChangeEvent( context.cursor, "octave", context.voice.octave )
