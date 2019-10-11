from .statement_node import StatementNode
from core import Instrument

class InstrumentDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, program ):
        super().__init__()

        self.name = name
        self.program = program

    def get_events ( self, context ):
        context.symbols.assign_instrument( Instrument( self.name, self.program ) )

        return iter(())
