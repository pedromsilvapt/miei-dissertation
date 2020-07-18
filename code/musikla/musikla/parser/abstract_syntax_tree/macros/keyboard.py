from musikla.parser.abstract_syntax_tree.statements.while_loop_node import WhileLoopStatementNode
from typing import Any, Dict, List, Optional, Tuple, cast
from musikla.core import Context, Value
from ..node import Node, ValueNode
from ..expressions import FunctionExpressionNode, StringLiteralNode, BoolLiteralNode, ListComprehensionNode, VariableExpressionNode, ArrayLiteralNode, BlockNode
from ..statements import ForLoopStatementNode, IfStatementNode, StatementsListNode, VariableDeclarationStatementNode
from .macro import MacroNode

ModifierNames = [ 'hold', 'extend', 'toggle', 'repeat', 'release' ]

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
    def __init__ ( self, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int, int] = None ):
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
    def __init__ ( self, shortcut : Node, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int, int] = None ):
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
    def __init__ ( self, comprehension : ListComprehensionNode, modifiers : List[str], args : List[str], expression : Node, position : Tuple[int, int, int] = None ):
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

class KeyboardForLoopMacroNode( MacroNode ):
    def __init__ ( self, variable : str, iterator : Node, shortcuts : List[MacroNode], position : Tuple[int, int, int] = None ):
        super().__init__( position )
    
        self.variable : str = variable
        self.iterator : Node = iterator
        self.shortcuts : List[MacroNode] = shortcuts

        body = StatementsListNode( [ macro.virtual_node for macro in self.shortcuts if macro.virtual_node is not None ] )

        self.virtual_node = ForLoopStatementNode( self.variable, self.iterator, body, position = position )

    def set_keyboard ( self, keyboard : Node ):
        for macro in self.shortcuts:
            cast( Any, macro ).set_keyboard( keyboard )

class KeyboardWhileLoopMacroNode( MacroNode ):
    def __init__ ( self, condition : Node, shortcuts : List[MacroNode], position : Tuple[int, int, int] = None ):
        super().__init__( position )
    
        self.condition : Node = condition
        self.shortcuts : List[MacroNode] = shortcuts

        body = StatementsListNode( [ macro.virtual_node for macro in self.shortcuts if macro.virtual_node is not None ] )

        self.virtual_node = WhileLoopStatementNode( self.condition, body, position = position )

    def set_keyboard ( self, keyboard : Node ):
        for macro in self.shortcuts:
            cast( Any, macro ).set_keyboard( keyboard )

class KeyboardIfMacroNode( MacroNode ):
    def __init__ ( self, condition : Node, shortcuts : List[MacroNode], else_shortcuts : List[MacroNode] = None, position : Tuple[int, int, int] = None ):
        super().__init__( position )
    
        self.condition : Node = condition
        self.shortcuts : List[MacroNode] = shortcuts
        self.else_shortcuts : List[MacroNode] = else_shortcuts

        body = StatementsListNode( [ macro.virtual_node for macro in self.shortcuts if macro.virtual_node is not None ] )
        else_body = StatementsListNode( [ macro.virtual_node for macro in self.else_shortcuts if macro.virtual_node is not None ] ) if else_shortcuts is not None else None

        self.virtual_node = IfStatementNode( self.condition, body, else_body, position = position )

    def set_keyboard ( self, keyboard : Node ):
        for macro in self.shortcuts:
            cast( Any, macro ).set_keyboard( keyboard )

        if self.else_shortcuts is not None:
            for macro in self.else_shortcuts:
                cast( Any, macro ).set_keyboard( keyboard )

class KeyboardBlockMacroNode( MacroNode ):
    def __init__ ( self, body : Node = None, position : Tuple[int, int, int] = None ):
        super().__init__( position )
    
        self.body : Optional[Node] = body

        self.virtual_node = self.body # StatementsListNode( [ macro.virtual_node for macro in self.body if macro.virtual_node is not None ] )

    def set_keyboard ( self, keyboard : Node ):
        pass

class KeyboardDeclarationMacroNode(MacroNode):
    def __init__ ( self, shortcuts : List[Node], flags : List[str] = None, prefix : Node = None, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        var_name = '__keyboard'

        # Clone the list so that our changes don't affect the original list
        shortcuts = list( shortcuts )

        for node in shortcuts:
            cast( Any, node ).set_keyboard( VariableExpressionNode( var_name ) )

        if flags:
            shortcuts.insert( 0, FunctionExpressionNode( VariableExpressionNode( "keyboard\\push_flags" ), cast( Any, [ VariableExpressionNode( var_name ) ] ) + [ StringLiteralNode( f ) for f in flags ] ) )
            shortcuts.append( FunctionExpressionNode( VariableExpressionNode( "keyboard\\pop_flags" ), cast( Any, [ VariableExpressionNode( var_name ) ] ) + [ StringLiteralNode( f ) for f in flags ] ) )

        if prefix:
            shortcuts.insert( 0, FunctionExpressionNode( VariableExpressionNode( "keyboard\\push_prefix" ), cast( Any, [ VariableExpressionNode( var_name ) ] ) + [ prefix ] ) )
            shortcuts.append( FunctionExpressionNode( VariableExpressionNode( "keyboard\\pop_prefix" ), cast( Any, [ VariableExpressionNode( var_name ) ] ) ) )

        shortcuts.insert( 0, VariableDeclarationStatementNode( var_name, FunctionExpressionNode( VariableExpressionNode( "keyboard\\create" ) ), local = True ) )
        shortcuts.append( VariableExpressionNode( var_name ) )

        self.virtual_node = BlockNode( StatementsListNode( shortcuts, position ) )

        # from musikla.parser import CodePrinter
        
        # print( CodePrinter().print( self.virtual_node ) )
