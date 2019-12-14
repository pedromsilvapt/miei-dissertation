from typing import List
from core import Context, Value
from ..node import Node
from ..expressions import FunctionExpressionNode, StringLiteralNode, BoolLiteralNode, ListComprehensionNode, VariableExpressionNode, BlockNode
from ..statements import ForLoopStatementNode, IfStatementNode, StatementsListNode, VariableDeclarationStatementNode
from .macro import MacroNode

ModifierNames = [ 'hold', 'extend', 'toggle', 'repeat' ]

def handle_modifiers ( modifiers : List[str] ) -> (dict, str):
    props = dict()

    rest = None

    for i in range( len( modifiers ) - 1, -1, -1 ):
        if modifiers[ i ] in ModifierNames:
            props[ modifiers[ i ] ] = True
        else:
            rest = '+'.join( modifiers[ 0:i + 1 ] )
            break
    
    return (props, rest)

class KeyboardShortcutMacroNode(MacroNode):
    def __init__ ( self, modifiers : List[str], expression : Node, position : (int, int) = None ):
        super().__init__( position )
        
        self.modifiers : List[str] = modifiers
        self.expression : Node = expression

        (kargs, shortcut) = handle_modifiers( modifiers )

        kargs = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs.items() )

        self.virtual_node : Node = FunctionExpressionNode( 
            "keyboard\\register", 
            [ None, StringLiteralNode( shortcut ), expression ], 
            kargs, 
            position = self.position
        )
    
    def set_keyboard ( self, keyboard : Node ):
        self.virtual_node.parameters[ 0 ] = keyboard

class KeyboardShortcutDynamicMacroNode(MacroNode):
    def __init__ ( self, shortcut : Node, modifiers : List[str], expression : Node, position : (int, int) = None ):
        super().__init__( position )
        
        self.shortcut : Node = shortcut
        self.modifiers : List[str] = modifiers
        self.expression : Node = expression

        (kargs, rest) = handle_modifiers( modifiers )

        kargs = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs.items() )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        self.virtual_node : Node = FunctionExpressionNode( 
            "keyboard\\register", 
            [ None, shortcut, expression ], 
            kargs, 
            position = self.position
        )

    def set_keyboard ( self, keyboard : Node ):
        self.virtual_node.parameters[ 0 ] = keyboard

class KeyboardShortcutComprehensionMacroNode(MacroNode):
    def __init__ ( self, comprehension : ListComprehensionNode, modifiers : List[str], expression : Node, position : (int, int) = None ):
        super().__init__( position )
        
        self.comprehension : ListComprehensionNode = comprehension
        self.modifiers : List[str] = modifiers
        self.expression : Node = expression

        (kargs, rest) = handle_modifiers( modifiers )

        kargs = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs.items() )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        node = FunctionExpressionNode( 
            "keyboard\\register", 
            [ None, self.comprehension.expression, expression ], 
            kargs
        )

        if self.comprehension.condition != None:
            node = IfStatementNode( self.comprehension.condition, node )

        self.virtual_node : Node = ForLoopStatementNode( 
            self.comprehension.variable, 
            self.comprehension.min, 
            self.comprehension.max,
            node,
            position = position
        )

    def set_keyboard ( self, keyboard : Node ):
        node = self.virtual_node.body

        if isinstance( node, IfStatementNode ):
            node = node.body
        
        node.parameters[ 0 ] = keyboard
    
class KeyboardDeclarationMacroNode(MacroNode):
    def __init__ ( self, shortcuts : List[Node], flags : List[str] = None, prefix : Node = None, position : (int, int) = None ):
        super().__init__( position )

        var_name = 'keyboard'

        # Clone the list so that our changes don't affect the original list
        shortcuts = list( shortcuts )

        for node in shortcuts:
            node.set_keyboard( VariableExpressionNode( var_name ) )

        if flags:
            shortcuts.insert( 0, FunctionExpressionNode( "keyboard\\push_flags", [ VariableExpressionNode( var_name ) ] + [ StringLiteralNode( f ) for f in flags ] ) )
            shortcuts.append( FunctionExpressionNode( "keyboard\\pop_flags", [ VariableExpressionNode( var_name ) ] + [ StringLiteralNode( f ) for f in flags ] ) )

        if prefix:
            shortcuts.insert( 0, FunctionExpressionNode( "keyboard\\push_prefix", [ VariableExpressionNode( var_name ) ] + [ prefix ] ) )
            shortcuts.append( FunctionExpressionNode( "keyboard\\pop_prefix", [ VariableExpressionNode( var_name ) ] ) )

        shortcuts.insert( 0, VariableDeclarationStatementNode( var_name, FunctionExpressionNode( "keyboard\\create" ), local = True ) )
        shortcuts.append( VariableExpressionNode( var_name ) )

        self.virtual_node = BlockNode( StatementsListNode( shortcuts, position ) )
