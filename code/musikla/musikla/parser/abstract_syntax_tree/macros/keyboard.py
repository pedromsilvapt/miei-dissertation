from typing import Any, Dict, List, Optional, Tuple, cast
from musikla.core import Context, Value
from ..node import Node, ValueNode
from ..expressions import FunctionExpressionNode, StringLiteralNode, BoolLiteralNode, ListComprehensionNode, VariableExpressionNode, ArrayLiteralNode, BlockNode
from ..statements import ForLoopStatementNode, IfStatementNode, StatementsListNode, VariableDeclarationStatementNode
from .macro import MacroNode

ModifierNames = [ 'hold', 'extend', 'toggle', 'repeat' ]

def handle_modifiers ( modifiers : List[str] ) -> Tuple[Dict[str, bool], Optional[str]]:
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
    def __init__ ( self, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.modifiers : List[str] = modifiers
        self.args : List[str] = args
        self.expression : Node = expression

        (kargs_raw, shortcut) = handle_modifiers( modifiers )

        kargs : Dict[str, Node] = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs_raw.items() )

        if self.args:
            kargs[ 'args' ] = ValueNode( self.args )

        self.virtual_node : Node = FunctionExpressionNode(
            VariableExpressionNode( "keyboard\\register" ),
            [ None, StringLiteralNode( shortcut ), expression ],
            kargs,
            position = self.position
        )

    def set_keyboard ( self, keyboard : Node ):
        cast( FunctionExpressionNode, self.virtual_node ).parameters[ 0 ] = keyboard

class KeyboardShortcutDynamicMacroNode(MacroNode):
    def __init__ ( self, shortcut : Node, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.shortcut : Node = shortcut
        self.modifiers : List[str] = modifiers
        self.args : List[str] = args
        self.expression : Node = expression

        (kargs_raw, rest) = handle_modifiers( modifiers )

        kargs : Dict[str, Node] = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs_raw.items() )
        
        if self.args:
            kargs[ 'args' ] = ValueNode( self.args )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        self.virtual_node : Node = FunctionExpressionNode( 
            VariableExpressionNode( "keyboard\\register" ), 
            [ None, shortcut, expression ], 
            kargs, 
            position = self.position
        )

    def set_keyboard ( self, keyboard : Node ):
        cast( FunctionExpressionNode, self.virtual_node ).parameters[ 0 ] = keyboard

class KeyboardShortcutComprehensionMacroNode(MacroNode):
    def __init__ ( self, comprehension : ListComprehensionNode, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int] = None ):
        super().__init__( position )
        
        self.comprehension : ListComprehensionNode = comprehension
        self.modifiers : List[str] = modifiers
        self.args : List[str] = args
        self.expression : Node = expression

        (kargs_raw, rest) = handle_modifiers( modifiers )

        kargs : Dict[str, Node] = dict( ( m, BoolLiteralNode( v ) ) for m, v in kargs_raw.items() )

        if rest != None:
            raise BaseException( "Keyboard shortcut with invalid modifiers: %s" % rest )

        if self.args:
            kargs[ 'args' ] = ValueNode( self.args )

        node = FunctionExpressionNode( 
            VariableExpressionNode( "keyboard\\register" ), 
            [ None, self.comprehension.expression, expression ], 
            kargs
        )

        if self.comprehension.condition != None:
            node = IfStatementNode( self.comprehension.condition, node )

        r = FunctionExpressionNode( VariableExpressionNode( "range" ), [ self.comprehension.min, self.comprehension.max ] )

        self.virtual_node : Node = ForLoopStatementNode( 
            self.comprehension.variable, 
            r,
            node, 
            position = position 
        )

    def set_keyboard ( self, keyboard : Node ):
        node = cast( ForLoopStatementNode, self.virtual_node ).body

        if isinstance( node, IfStatementNode ):
            node = node.body
        
        cast( FunctionExpressionNode, node ).parameters[ 0 ] = keyboard

class KeyboardDeclarationMacroNode(MacroNode):
    def __init__ ( self, shortcuts : List[Node], flags : List[str] = None, prefix : Node = None, position : Tuple[int, int] = None ):
        super().__init__( position )

        var_name = 'keyboard'

        # Clone the list so that our changes don't affect the original list
        shortcuts = list( shortcuts )

        for node in shortcuts:
            cast( Any, node ).set_keyboard( VariableExpressionNode( var_name ) )

        if flags:
            shortcuts.insert( 0, FunctionExpressionNode( VariableExpressionNode( "keyboard\\push_flags" ), [ VariableExpressionNode( var_name ) ] + [ StringLiteralNode( f ) for f in flags ] ) )
            shortcuts.append( FunctionExpressionNode( VariableExpressionNode( "keyboard\\pop_flags" ), [ VariableExpressionNode( var_name ) ] + [ StringLiteralNode( f ) for f in flags ] ) )

        if prefix:
            shortcuts.insert( 0, FunctionExpressionNode( VariableExpressionNode( "keyboard\\push_prefix" ), [ VariableExpressionNode( var_name ) ] + [ prefix ] ) )
            shortcuts.append( FunctionExpressionNode( VariableExpressionNode( "keyboard\\pop_prefix" ), [ VariableExpressionNode( var_name ) ] ) )

        shortcuts.insert( 0, VariableDeclarationStatementNode( var_name, FunctionExpressionNode( VariableExpressionNode( "keyboard\\create" ) ), local = True ) )
        shortcuts.append( VariableExpressionNode( var_name ) )

        self.virtual_node = BlockNode( StatementsListNode( shortcuts, position ) )
