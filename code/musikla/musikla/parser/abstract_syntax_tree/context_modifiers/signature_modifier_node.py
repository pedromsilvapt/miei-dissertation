from musikla.parser.printer import CodePrinter
from typing import Tuple
from .context_modifier_node import ContextModifierNode
from musikla.core.events import ContextChangeEvent
from musikla.core import Context, Voice

class SignatureModifierNode( ContextModifierNode ):
    def __init__ ( self, upper = None, lower = None, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.upper = upper
        self.lower = lower

    def apply ( self, voice : Voice ):
        if self.upper != None or self.lower != None:
            voice.time_signature = ( self.upper, self.lower )
        elif self.upper != None:
            voice.time_signature = ( self.upper, voice.time_signature[ 1 ] )
        elif self.lower != None:
            voice.time_signature = ( voice.time_signature[ 0 ], self.lower )

    def modify ( self, context : Context ):
        if self.upper != None or self.lower != None:
            context.voice = context.voice.clone( time_signature = ( self.upper, self.lower ) )
        elif self.upper != None:
            context.voice = context.voice.clone( time_signature = ( self.upper, context.time_signature[ 1 ] ) )
        elif self.lower != None:
            context.voice = context.voice.clone( time_signature = ( context.time_signature[ 0 ], self.lower ) )

        yield ContextChangeEvent( context.cursor, "timeSignature", context.voice.time_signature, context.voice, 0 )
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'S' + str( self.upper ) + '/' + str( self.lower ) )
