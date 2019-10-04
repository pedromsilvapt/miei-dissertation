from .context_modifier_node import ContextModifierNode

class VelocityModifierNode( ContextModifierNode ):
    def __init__ ( self, velocity ):
        super().__init__()

        self.velocity = velocity

    def modify ( self, context ):
        context.velocity = self.velocity;
