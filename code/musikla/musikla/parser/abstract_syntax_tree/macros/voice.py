from ..statements import StatementNode, VariableDeclarationStatementNode
from ..expressions import FunctionExpressionNode, StringLiteralNode, VariableExpressionNode
from .macro import MacroNode
from musikla.core import Instrument

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
            FunctionExpressionNode( VariableExpressionNode( "voices\\create" ), [ StringLiteralNode( name ) ], kargs )
        )
