from .statement_node import StatementNode
from core import Instrument

class InstrumentDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, program, position : (int, int) = None ):
        super().__init__( position )

        self.name = name
        self.program = program


    def eval ( self, context, assignment : bool = False ):
        context.symbols.assign_instrument( Instrument( self.name, self.program ) )
        
        return None
