from typing import Tuple
from .block_context_modifier_node import BlockContextModifierNode
from musikla.core.events import ProgramChangeEvent
from musikla.core import Value, Voice, Context, TemplateMusic

class VoiceBlockModifier( BlockContextModifierNode ):
    def __init__ ( self, body, voice_name : str, position : Tuple[int, int] = None ):
        super().__init__( body, position )

        self.voice_name : str = voice_name

    def modify ( self, context ):
        voice : Voice = context.symbols.lookup( self.voice_name )

        Value.expect( voice, Voice, "Voice modifier " + self.voice_name )
        
        context.voice = voice

    def restore ( self, context ):
        pass

    def eval ( self, context : Context ):
        if self.voice_name == '?':
            return TemplateMusic( self.body )
        else:
            return super().eval( context )
