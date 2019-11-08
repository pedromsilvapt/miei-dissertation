from typing import List
from core import Context, Value
from ..node import Node
from ..expressions import FunctionExpressionNode, StringLiteralNode, BoolLiteralNode, ListComprehensionNode
from ..statements import ForLoopStatementNode, IfStatementNode, StatementsListNode

class MacroNode(Node):
    def eval ( self, context : Context, assignment : bool = False ):
        return self.virtual_node.eval( context, assignment = assignment )

ModifierNames = [ 'hold', 'release', 'toggle', 'repeat' ]

def handle_modifiers ( modifiers : List[str] ) -> (dict, str):
    props = dict( (m, False) for m in ModifierNames )

    rest = None

    for i in range( len( modifiers ) - 1, -1, -1 ):
        if modifiers[ i ] in props:
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
            [ StringLiteralNode( shortcut ), expression ], 
            kargs, 
            position = self.position
        )

class KeyboardShortcutDynamicMacroNode(MacroNode):
    def __init__ ( self, shortcut : Node, modifiers : List[str], expression : Node, position : (int, int) = None ):
        super().__init__( position )
        
        self.shortcut : Node = shortcut
        self.modifiers : List[str] = modifiers
        self.expression : Node = expression

        (kargs, rest) = handle_modifiers( modifiers )

        kargs = dict( ( m, Value.create( v ) ) for m, v in kargs.items() )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        self.virtual_node : Node = FunctionExpressionNode( 
            "keyboard\\register", 
            [ shortcut, expression ], 
            kargs, 
            position = self.position
        )

class KeyboardShortcutComprehensionMacroNode(MacroNode):
    def __init__ ( self, comprehension : ListComprehensionNode, modifiers : List[str], expression : Node, position : (int, int) = None ):
        super().__init__( position )
        
        self.comprehension : ListComprehensionNode = comprehension
        self.modifiers : List[str] = modifiers
        self.expression : Node = expression

        (kargs, rest) = handle_modifiers( modifiers )

        kargs = dict( ( m, Value.create( v ) ) for m, v in kargs.items() )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        node = FunctionExpressionNode( 
            "keyboard\\register", 
            [ self.comprehension.expression, expression ], 
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
    
class KeyboardDeclarationMacroNode(MacroNode):
    def __init__ ( self, shortcuts : List[Node], position : (int, int) = None ):
        super().__init__( position )
        
        self.virtual_node = StatementsListNode( shortcuts, position )
