from .context_modifier_node import ContextModifierNode

class LengthModifierNode( ContextModifierNode ):
    def __init__ ( self, length ):
        super().__init__()

        self.length = length
        
    def modify ( self, context ):
        context.value = self.length;
