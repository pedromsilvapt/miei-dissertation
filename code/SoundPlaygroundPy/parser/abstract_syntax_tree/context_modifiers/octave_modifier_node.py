from .context_modifier_node import ContextModifierNode

class OctaveModifierNode( ContextModifierNode ):
    def __init__ ( self, octave ):
        super().__init__()

        self.octave = octave
        
    def modify ( self, context ):
        context.octave = self.octave
