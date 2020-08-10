import sys
from typing import Any, List, Optional, Tuple, cast
from lark import Lark, Transformer, v_args
from musikla.core.theory import NoteAccidental, Note, Chord
from .abstract_syntax_tree import PythonNode
from .abstract_syntax_tree import NoteNode, ChordNode, MusicSequenceNode, MusicParallelNode, RestNode
from .abstract_syntax_tree.context_modifiers import LengthModifierNode, OctaveModifierNode, SignatureModifierNode, VelocityModifierNode, InstrumentModifierNode, TempoModifierNode, VoiceBlockModifier

from .abstract_syntax_tree.expressions import VariableExpressionNode, FunctionExpressionNode, FunctionChainExpressionNode, ListComprehensionNode
from .abstract_syntax_tree.expressions import StringLiteralNode, NumberLiteralNode, BoolLiteralNode, NoneLiteralNode
from .abstract_syntax_tree.expressions import ObjectLiteralNode, ArrayLiteralNode

from .abstract_syntax_tree.expressions import PlusBinaryOperatorNode, MinusBinaryOperatorNode, PowBinaryOperatorNode, MultBinaryOperatorNode, DivBinaryOperatorNode
from .abstract_syntax_tree.expressions import AndLogicOperatorNode, OrLogicOperatorNode

from .abstract_syntax_tree.expressions import GreaterComparisonOperatorNode, GreaterEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import EqualComparisonOperatorNode, NotEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import LesserComparisonOperatorNode, LesserEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import IsComparisonOperatorNode, IsNotComparisonOperatorNode
from .abstract_syntax_tree.expressions import InComparisonOperatorNode, NotInComparisonOperatorNode

from .abstract_syntax_tree.expressions import NotOperatorNode, GroupNode, BlockNode, PropertyAccessorNode

from .abstract_syntax_tree.statements import StatementsListNode, VariableDeclarationStatementNode, MultiVariableDeclarationStatementNode, FunctionDeclarationStatementNode
from .abstract_syntax_tree.statements import ForLoopStatementNode, WhileLoopStatementNode, IfStatementNode, ReturnStatementNode, ImportStatementNode

from .abstract_syntax_tree.macros import KeyboardDeclarationMacroNode, KeyboardShortcutMacroNode, KeyboardShortcutDynamicMacroNode, KeyboardShortcutComprehensionMacroNode, KeyboardForLoopMacroNode, KeyboardWhileLoopMacroNode, KeyboardIfMacroNode, KeyboardBlockMacroNode
from .abstract_syntax_tree.macros import VoiceDeclarationMacroNode

from fractions import Fraction

def isnumber ( n ):
    return type( n ) is int or type( n ) is float or isinstance( n, Fraction )

@v_args( tree = True )
class MusiklaTransformer(Transformer):
    def __init__(self, file : str = None, file_id : int = None, visit_tokens : bool = True):
        super().__init__(visit_tokens)

        self.file : Optional[str] = file
        self.file_id : Optional[int] = file_id

    def _get_position ( self, node, end_node = None ) -> Tuple[int, int, int]:
        end_pos = end_node.position[ 2 ] if end_node is not None and end_node.position is not None else node.meta.end_pos

        return ( self.file_id if self.file_id is not None else -1, node.meta.start_pos, end_pos )

    def start ( self, tree ):
        body = tree.children[ 0 ]

        if body is None:
            body = StatementsListNode([], position = self._get_position( tree ))

        if tree.children[ 1 ] is not None:
            if not isinstance( body, StatementsListNode ):
                body = StatementsListNode( [ body ], position = self._get_position( tree ) )

            body.statements.insert( 0, tree.children[ 1 ] )
        
        return body

    def body ( self, tree ):
        position = self._get_position( tree )

        children = list( tree.children )

        if any( ( c.hoisted for c in children ) ):
            children = [
                *filter( lambda c: c.hoisted, children ),
                *filter( lambda c: not c.hoisted, children )
            ]

        return StatementsListNode( children, position = position )


    def python ( self, tree ):
        position = self._get_position( tree )

        return PythonNode( tree.children[ 0 ], False, position = position )

    def assignment ( self, tree ):
        position = self._get_position( tree )

        operator = tree.children[ 1 ][ :-1 ]

        return VariableDeclarationStatementNode( tree.children[ 0 ], tree.children[ 2 ], operator = operator, position = position )

    def multi_assignment ( self, tree ):
        position = self._get_position( tree )

        operator = tree.children[ -2 ][ :-1 ]

        return MultiVariableDeclarationStatementNode( tree.children[ :-2 ], tree.children[ -1 ], operator = operator, position = position )

    def voice_assignment ( self, tree ):
        position = self._get_position( tree )

        name = tree.children[ 0 ]
        modifiers, parent = tree.children[ 1 ]
        
        return VoiceDeclarationMacroNode( 
            name, modifiers, parent,
            position = position
        )
    
    def voice_assignment_inherit ( self, tree ):
        return ( tree.children[ 1 ], VariableExpressionNode( tree.children[ 0 ] ) )
    
    def voice_assignment_base ( self, tree ):
        return ( tree.children[ 0 ], None )

    def import_global ( self, tree ):
        position = self._get_position( tree )

        return ImportStatementNode( tree.children[ 0 ], False, position = position )

    def import_local ( self, tree ):
        position = self._get_position( tree )

        return ImportStatementNode( tree.children[ 0 ], True, position = position )

    def for_variables ( self, tree ):
        return list( tree.children )

    def for_loop_head_range ( self, tree ):
        expression = FunctionExpressionNode( VariableExpressionNode( "range" ), [ tree.children[ 1 ], tree.children[ 2 ] ] )

        return ( tree.children[ 0 ], expression )

    def for_loop_head ( self, tree ):
        return ( tree.children[ 0 ], tree.children[ 1 ] )

    def for_loop_statement ( self, tree ):
        position = self._get_position( tree )

        variables, expression = tree.children[ 0 ]

        return ForLoopStatementNode( variables, expression, tree.children[ 1 ], position )

    def while_loop_statement ( self, tree ):
        position = self._get_position( tree )

        return WhileLoopStatementNode( tree.children[ 0 ], tree.children[ 1 ], position )

    def visit_while_loop_statement ( self, node, children ):
        position = self._get_position( node )

        return WhileLoopStatementNode( children.expression[ 0 ], children.body[ 0 ], position )
    
    def if_statement_else ( self, tree ):
        position = self._get_position( tree )

        return IfStatementNode( tree.children[ 0 ], tree.children[ 1 ], tree.children[ 2 ], position )

    def if_statement ( self, tree ):
        position = self._get_position( tree )

        return IfStatementNode( tree.children[ 0 ], tree.children[ 1 ], position = position )

    def if_body ( self, tree ):
        return tree.children[ 0 ]if tree.children else None

    def return_statement ( self, tree ):
        position = self._get_position( tree )

        if tree.children:
            return ReturnStatementNode( tree.children[ 0 ], position = position )

        return ReturnStatementNode( position = position )

    def parallel ( self, tree ):
        position = self._get_position( tree )

        return MusicParallelNode( list( tree.children ), position )

    def sequence ( self, tree ):
        position = self._get_position( tree )

        return MusicSequenceNode( list( tree.children ), position )

    def and_logic_op ( self, tree ):
        return AndLogicOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def or_logic_op ( self, tree ):
        return OrLogicOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def gte_comparison_op ( self, tree ):
        return GreaterEqualComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def gt_comparison_op ( self, tree ):
        return GreaterComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )
        
    def eq_comparison_op ( self, tree ):
        return EqualComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def neq_comparison_op ( self, tree ):
        return NotEqualComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def lte_comparison_op ( self, tree ):
        return LesserEqualComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def lt_comparison_op ( self, tree ):
        return LesserComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def isnot_comparison_op ( self, tree ):
        return IsNotComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )
        
    def is_comparison_op ( self, tree ):
        return IsComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def in_comparison_op ( self, tree ):
        return InComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def notin_comparison_op ( self, tree ):
        return NotInComparisonOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def sum_op ( self, tree ):
        return PlusBinaryOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def sub_op ( self, tree ):
        return MinusBinaryOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def pow_op ( self, tree ):
        return PowBinaryOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def mult_op ( self, tree ):
        return MultBinaryOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def div_op ( self, tree ):
        return DivBinaryOperatorNode( tree.children[ 0 ], tree.children[ 1 ], position = self._get_position( tree ) )

    def negation ( self, tree ):
        return NotOperatorNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def accessor ( self, tree ):
        position = self._get_position( tree )

        expression = tree.children[ 0 ]
        accessor = tree.children[ 1 ]

        accessor.expression = expression
        accessor.position = position

        return accessor

    def method_call ( self, tree ):
        f, s, e = self._get_position( tree )

        property = self.property_accessor( tree )

        fn_call = tree.children[ 1 ]
        
        return FunctionChainExpressionNode( property, fn_call, position = ( f, s, e ) )

    def index_call ( self, tree ):
        f, s, e = self._get_position( tree )
        
        expression = tree.children[ 0 ]
        
        fn_call = tree.children[ 1 ]

        property = PropertyAccessorNode( cast( Any, None ), expression, False, position = (f, s, fn_call.position[ 2 ] - 1) )
        
        return FunctionChainExpressionNode( property, fn_call, position = ( f, s, e ) )

    def property_accessor ( self, tree ):
        s, f, _ = self._get_position( tree )
        
        identifier = StringLiteralNode( tree.children[ 0 ], position = (f, s, len( tree.children[ 0 ] ) ) )

        return PropertyAccessorNode( cast( Any, None ), identifier, True, position = identifier.position )

    def index_accessor ( self, tree ):
        position = self._get_position( tree )
        
        expression = tree.children[ 0 ]
        
        return PropertyAccessorNode( cast( Any, None ), expression, False, position = position )
        
    def python_expression ( self, tree ):
        position = self._get_position( tree )

        return PythonNode( tree.children[ 0 ], True, position = position )

    def function ( self, tree ):
        name = tree.children[ 0 ]

        fn_call = tree.children[ 1 ]

        _, s, _ = self._get_position( tree )
        f, _, e = fn_call.position

        fn_call.expression = VariableExpressionNode( name )
        fn_call.position = (f, s, e)

        return fn_call

    def function_call ( self, tree ):
        position = self._get_position( tree )
        
        positional, named = tree.children[ 0 ] or ([], {})
        
        return FunctionExpressionNode( None, positional, named, position )
        
    def function_call_chain ( self, tree ):
        _, s, _ = self._get_position( tree )

        right_hand = tree.children[ 1 ]
        f, rs, e = right_hand.position

        positional, named = tree.children[ 0 ] or ([], {})
        left_hand = FunctionExpressionNode( None, positional, named, (f, s, rs - 1) )
        
        return FunctionChainExpressionNode( left_hand, right_hand, (f, s, e) )

    def function_parameters ( self, tree ):
        positional = []
        named = {}

        for node in tree.children:
            if node.data == 'named_parameter':
                named[ node.children[ 0 ] ] = node.children[ 1 ]
            else:
                positional.append( node.children[ 0 ] )
        
        return positional, named

    def keyboard_declaration ( self, tree ):
        if len( tree.children ) == 3:
            return KeyboardDeclarationMacroNode( tree.children[ 2 ], tree.children[ 0 ], tree.children[ 1 ] )

        return KeyboardDeclarationMacroNode( tree.children[ 1 ], tree.children[ 0 ] )

    def keyboard_flags ( self, tree ):
        return list( tree.children )

    def keyboard_body ( self, tree ):
        return list( tree.children )

    def keyboard_for ( self, tree ):
        position = self._get_position( tree )
        
        var_name, expression = tree.children[ 0 ]

        return KeyboardForLoopMacroNode( var_name, expression, tree.children[ 1 ] or [], position = position )
    
    def keyboard_while ( self, tree ):
        position = self._get_position( tree )

        return KeyboardWhileLoopMacroNode( tree.children.expression, tree.children[ 1 ] or [], position = position )
    
    def keyboard_if ( self, tree ):
        position = self._get_position( tree )
        
        else_body = tree.children[ 2 ] if len( tree.children ) > 2 else None

        return KeyboardIfMacroNode( tree.children[ 0 ], tree.children[ 1 ] or [], else_body, position = position )
    
    def keyboard_block ( self, tree ):
        position = self._get_position( tree )
        
        return KeyboardBlockMacroNode( tree.children[ 0 ] if tree.children else None, position = position )

    def keyboard_shortcut ( self, tree ):
        position = self._get_position( tree )

        kind, key, flags = tree.children[ 0 ]

        expr = tree.children[ 2 ]

        args = tree.children[ 1 ]

        if kind == KeyboardShortcutComprehensionMacroNode:
            return KeyboardShortcutComprehensionMacroNode( key, flags, args, expr, position )
        elif kind == KeyboardShortcutDynamicMacroNode:
            return KeyboardShortcutDynamicMacroNode( key, flags, args, expr, position )
        else:
            return KeyboardShortcutMacroNode( key, args, expr, position )

    def keyboard_shortcut_key_static ( self, tree ):
        return (
            KeyboardShortcutMacroNode,
            list( tree.children ),
            None
        )

    def keyboard_shortcut_key_string ( self, tree ):
        return (
            KeyboardShortcutDynamicMacroNode,
            StringLiteralNode(tree.children[ 0 ]),
            list( tree.children[ 1: ] )
        )

    def keyboard_shortcut_key_dynamic ( self, tree ):
        return (
            KeyboardShortcutDynamicMacroNode,
            tree.children[ 0 ],
            list( tree.children[ 1: ] )
        )
    
    def keyboard_arguments ( self, tree ):
        if tree.children:
            return list( tree.children )
        
        return []

    def function_statements ( self, tree ):
        position = self._get_position( tree )

        name = tree.children[ 0 ]

        using = tree.children[ 2 ]

        body = tree.children[ 3 ]

        return FunctionDeclarationStatementNode( name, tree.children[ 1 ] or [], body, using, position )

    def function_expression ( self, tree ):
        position = self._get_position( tree )

        name = tree.children[ 0 ]
        
        using = tree.children[ 2 ]

        body = StatementsListNode( [ tree.children[ 3 ] ] )

        return FunctionDeclarationStatementNode( name, tree.children[ 1 ] or [], body, using, position )
    
    def using ( self, tree ):
        return list( tree.children )

    def arguments ( self, tree ):
        return list( tree.children )
    
    def argument_default ( self, tree ):
        return ( tree.children[ 1 ], tree.children[ 0 ], tree.children[ 2 ] )

    def argument ( self, tree ):
        return ( tree.children[ 1 ], tree.children[ 0 ], None )

    def argument_prefix ( self, tree ):
        return tree.children[ 0 ]

    def block ( self, tree ):
        position = self._get_position( tree )
        
        if not tree.children:
            return BlockNode( None, position = position )
        
        return BlockNode( tree.children[ 0 ], position = position )

    def block_call ( self, tree ):
        f, s, e = self._get_position( tree )
        
        if len( tree.children ) == 1:
            fn_call = tree.children[ 0 ]

            block = BlockNode( None )
        else:
            fn_call = tree.children[ 1 ]

            block = BlockNode( tree.children[ 0 ] )

        _, fs, fe = fn_call.position

        fn_call.expression = block
        fn_call.position = (f, s, fe)
        block.position = (f, s, fs - 1)

        return fn_call
        
    def group ( self, tree ):
        position = self._get_position( tree )
        
        return GroupNode( tree.children[ 0 ], position = position )

    def group_call ( self, tree ):
        f, s, e = self._get_position( tree )
        
        fn_call = tree.children[ 1 ]

        group = GroupNode( tree.children[ 0 ] )

        _, fs, fe = fn_call.position

        fn_call.expression = group
        fn_call.position = (f, s, fe)
        group.position = (f, s, fs - 1)

        return fn_call

    def string_literal ( self, tree ):
        position = self._get_position( tree )
        
        return StringLiteralNode( tree.children[ 0 ], position = position )
    
    def integer_literal ( self, tree ):
        position = self._get_position( tree )
        
        return NumberLiteralNode( tree.children[ 0 ], position = position )

    def float_literal ( self, tree ):
        position = self._get_position( tree )
        
        return NumberLiteralNode( tree.children[ 0 ], position = position )

    def bool_literal ( self, tree ):
        position = self._get_position( tree )
        
        return BoolLiteralNode( tree.children[ 0 ] == "true", position )

    def none_literal ( self, tree ):
        position = self._get_position( tree )

        return NoneLiteralNode( position )

    def array_literal ( self, tree ):
        position = self._get_position( tree )

        return ArrayLiteralNode( list( tree.children ), position = position )

    def object_literal ( self, tree ):
        position = self._get_position( tree )

        return ObjectLiteralNode( list( tree.children ), position = position )

    def object_item ( self, tree ):
        return ( tree.children[0], tree.children[1] )

    def object_key ( self, tree ):
        return tree.children[ 0 ]

    def chord_shortcut ( self, tree ):
        position = self._get_position( tree )
        
        value = Fraction( 1 )

        if len( tree.children ) == 3:
            value = tree.children[ 2 ]

        accidental, ( pitch_class, octave ) = tree.children[ 0 ]

        chord = tree.children[ 1 ]

        note = Note( 
            pitch_class = pitch_class,
            octave = octave,
            value = value,
            accidental = accidental
        )

        return ChordNode( Chord.from_abbreviature( note, chord, value ), position = position )

    def chord_manual ( self, tree ):
        position = self._get_position( tree )
        
        value = Fraction( 1 )

        x = len( tree.children )

        if tree.children and isnumber( tree.children[ -1 ] ):
            value = tree.children[ -1 ]
            x = -1

        notes : List[Note] = []

        for accidental, ( pitch_class, octave ) in tree.children[:x]:
            notes.append( Note( 
                pitch_class = pitch_class,
                octave = octave,
                value = value,
                accidental = accidental
            ) )

        return ChordNode( Chord( notes, None, value ), position = position )

    def CHORD_SUFFIX ( self, token ):
        return str( token )

    def rest ( self, tree ):
        position = self._get_position( tree )

        if tree.children:
            return RestNode( value = tree.children[ 0 ], visible = True, position = position )

        return RestNode( visible = True, position = position )

    def note ( self, tree ):
        position = self._get_position( tree )

        accidental, ( pitch_class, octave ) = tree.children[ 0 ]
        
        value = Fraction( 1 )

        if len( tree.children ) == 2:
            value = tree.children[ 1 ]
         
        note = Note( 
            pitch_class = pitch_class,
            octave = octave,
            value = value,
            accidental = accidental
        )

        return NoteNode( note, position )

    def note_value_int ( self, tree ):
        return tree.children[ 0 ]

    def note_value_frac ( self, tree ):
        if len( tree.children ) == 2:
            return Fraction( tree.children[ 0 ], tree.children[ 1 ] )
        else:
            return Fraction( 1, tree.children[ 0 ] )

    def note_pitch ( self, tree ):
        if len( tree.children ) == 1:
            return ( NoteAccidental.NONE, tree.children[ 0 ] )    

        return ( tree.children[ 0 ], tree.children[ 1 ] )

    def NOTE_ACCIDENTAL ( self, token ):
        if token == '^^':
            return NoteAccidental.DOUBLESHARP
        elif token == '^':
            return NoteAccidental.SHARP
        elif token == '_':
            return NoteAccidental.FLAT
        elif token == '__':
            return NoteAccidental.DOUBLEFLAT
        else:
            return NoteAccidental.NONE

    def NODE_PITCH_RAW ( self, token ):
        return Note.parse_pitch_octave( str( token ) )

    def tempo_mod ( self, tree ):
        return TempoModifierNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def velocity_mod ( self, tree ):
        return VelocityModifierNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def instrument_mod ( self, tree ):
        return InstrumentModifierNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def length_mod ( self, tree ):
        return LengthModifierNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def signature_mod ( self, tree ):
        position = self._get_position( tree )
        
        if len( tree.children ) == 2:
            return SignatureModifierNode( tree.children[ 0 ], tree.children[ 1 ], position )
        else:
            return SignatureModifierNode( lower = tree.children[ 1 ], position = position )

    def octave_mod ( self, tree ):
        return OctaveModifierNode( tree.children[ 0 ], position = self._get_position( tree ) )

    def voice_modifier ( self, tree ):
        position = self._get_position( tree )

        return VoiceBlockModifier( tree.children[ 1 ], tree.children[ 0 ], position = position )

    def VOICE_CALL ( self, token ):
        return token[1:-1]

    def VOICE_IDENTIFIER ( self, token ):
        return token[1:]

    def variable_call ( self, tree ):
        fn_call = tree.children[ 1 ]

        fn_call.position = self._get_position( tree, fn_call )

        fn_call.expression = VariableExpressionNode( tree.children[ 0 ] )

        return fn_call

    def variable_name ( self, tree ):
        position = self._get_position( tree )

        return VariableExpressionNode( tree.children[ 0 ], position = position )

    def FUNCTION_CALL ( self, token ):
        return token[:-1]

    def VARIABLE_CALL ( self, token ):
        return token[1:-1]

    def NAMED_IDENTIFIER ( self, token ):
        return token.strip( " \t\r\n=" )

    def VARIABLE_NAME ( self, token ):
        return token[1:]

    def IDENTIFIER ( self, token ):
        return str( token )

    def ALPHANUMERIC ( self, token ):
        return str( token )

    def INTEGER ( self, token ):
        return int( token )

    def FLOAT ( self, token ):
        return float( token )

    def STRING ( self, token ):
        return StringLiteralNode.escaped( token[1:-1], quote = token[ 0 ] )
