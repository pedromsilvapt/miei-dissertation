from .context_modifier_node import ContextModifierNode

class TempoModifierNode( ContextModifierNode ):
    def __init__ ( self, tempo ):
        super().__init__()

        self.tempo = tempo

    def modify ( self, context ):
        context.tempo = self.tempo
