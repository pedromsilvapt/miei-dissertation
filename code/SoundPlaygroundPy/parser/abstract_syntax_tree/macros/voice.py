from ..statements import StatementNode, VariableDeclarationStatementNode
from ..expressions import FunctionExpressionNode, StringLiteralNode
from .macro import MacroNode
from core import Instrument

class VoiceDeclarationMacroNode( MacroNode ):
    def __init__ ( self, name, program = None, modifiers = None, parent = None, position : (int, int) = None ):
        super().__init__( position )

        self.name = name

        kargs = {}

        if program != None:
            kargs[ 'instrument' ] = program
        
        if modifiers != None:
            kargs[ 'modifiers' ] = modifiers
        
        if parent != None:
            kargs[ 'inherit' ] = parent
 
        self.virtual_node = VariableDeclarationStatementNode(
            self.name,
            FunctionExpressionNode( "voices\\create", [ StringLiteralNode( name ) ], kargs )
        )
