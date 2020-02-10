from pathlib import Path
from arpeggio.peg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree
from musikla.core.events import NoteEvent
from musikla.core.theory import scales, NoteAccidental, Note
from .abstract_syntax_tree import Node
from .abstract_syntax_tree import NoteNode, MusicSequenceNode, MusicParallelNode, RestNode
from .abstract_syntax_tree.context_modifiers import LengthModifierNode, OctaveModifierNode, SignatureModifierNode, VelocityModifierNode, TempoModifierNode, VoiceBlockModifier

from .abstract_syntax_tree.expressions import VariableExpressionNode, FunctionExpressionNode, ListComprehensionNode
from .abstract_syntax_tree.expressions import StringLiteralNode, NumberLiteralNode, BoolLiteralNode, NoneLiteralNode

from .abstract_syntax_tree.expressions import PlusBinaryOperatorNode, MinusBinaryOperatorNode, MultBinaryOperatorNode, DivBinaryOperatorNode
from .abstract_syntax_tree.expressions import AndLogicOperatorNode, OrLogicOperatorNode

from .abstract_syntax_tree.expressions import GreaterComparisonOperatorNode, GreaterEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import EqualComparisonOperatorNode, NotEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import LesserComparisonOperatorNode, LesserEqualComparisonOperatorNode

from .abstract_syntax_tree.expressions import NotOperatorNode, GroupNode, BlockNode

from .abstract_syntax_tree.statements import StatementsListNode, VariableDeclarationStatementNode, FunctionDeclarationStatementNode
from .abstract_syntax_tree.statements import ForLoopStatementNode, WhileLoopStatementNode, IfStatementNode

from .abstract_syntax_tree.macros import KeyboardDeclarationMacroNode, KeyboardShortcutMacroNode, KeyboardShortcutDynamicMacroNode, KeyboardShortcutComprehensionMacroNode
from .abstract_syntax_tree.macros import VoiceDeclarationMacroNode

from fractions import Fraction

class ParserVisitor(PTNodeVisitor):
    def visit_body ( self, node, children ):
        children = children.statement
        
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        return StatementsListNode( list( children ), position )

    def visit_comment ( self, node, children ):
        return None

    def visit_statement ( self, node, children ):
        return children[ 0 ]

    def visit_var_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        return VariableDeclarationStatementNode( children[ 0 ], children[ 1 ], position = position )

    def visit_voice_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        name = children.identifier[ 0 ]
        args = children.voice_declaration_body[ 0 ]
        
        return VoiceDeclarationMacroNode( 
            name, args[ 0 ], args[ 1 ], args[ 2 ],
            position = position 
        )
    
    def visit_voice_declaration_body ( self, node, children ):
        instrument = None
        modifiers = None
        parent = None

        if children.function_parameters:
            params = children.function_parameters[ 0 ]

            instrument = params[ 0 ]
            
            if len( params ) > 1:
                modifiers = params[ 1 ]

        if children.identifier:
            parent = VariableExpressionNode( children.identifier[ 0 ] ) 

        if children.integer:
            instrument = NumberLiteralNode( children.integer[ 0 ] )

        return ( instrument, modifiers, parent )

    def visit_function_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 3:
            return FunctionDeclarationStatementNode( children[ 0 ], children[ 1 ], children[ 2 ], position )

        return FunctionDeclarationStatementNode( children[ 0 ], [], children[ 1 ], position )
    
    def visit_arguments ( self, node, children ):
        return list( children )
    
    def visit_single_argument ( self, node, children ):
        return children[ 0 ]

    def visit_single_argument_expr ( self, node, children ):
        return ( children[ 0 ], "expr" )
    
    def visit_single_argument_ref ( self, node, children ):
        return ( children[ 0 ], "ref" )

    def visit_single_argument_eval ( self, node, children ):
        return ( children[ 0 ], None )

    def visit_for_loop_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        return ForLoopStatementNode( children.namespaced[ 0 ], children.value_expression[ 0 ], children.value_expression[ 1 ], children.body[ 0 ], position )

    def visit_while_loop_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        return WhileLoopStatementNode( children.expression[ 0 ], children.body[ 0 ], position )
    
    def visit_if_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children.body ) == 2:
            return IfStatementNode( children.expression[ 0 ], children.body[ 0 ], children.body[ 1 ], position )

        return IfStatementNode( children.expression[ 0 ], children.body[ 0 ], position = position )

    def visit_keyboard_declaration ( self, node, children ):
        if len( children.group ):
            return KeyboardDeclarationMacroNode( list( children.keyboard_shortcut ), list( children.alphanumeric ), children.group[ 0 ].expression )

        return KeyboardDeclarationMacroNode( list( children.keyboard_shortcut ), list( children.alphanumeric ) )

    def visit_keyboard_shortcut ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children.list_comprehension ) == 1:
            return KeyboardShortcutComprehensionMacroNode(
                children.list_comprehension[ 0 ],
                list( children.alphanumeric ),
                children.expression[ 0 ],
                position
            )
        elif len( children.value_expression ) == 1 or len( children.string_value ) == 1:
            if children.string_value:
                variable = children.string_value[ 0 ]
            else:
                variable = children.value_expression[ 0 ]

            return KeyboardShortcutDynamicMacroNode(
                variable,
                list( children.alphanumeric ),
                children.expression[ 0 ],
                position
            )
        else:
            return KeyboardShortcutMacroNode(
                list( children.alphanumeric ),
                children.expression[ 0 ],
                position
            )

    def visit_list_comprehension ( self, node, children ):
        position = ( node.position, node.position_end )

        expression = children.expression[ 0 ]
        name = children.namespaced[ 0 ]
        min = children.value_expression[ 0 ]
        max = children.value_expression[ 1 ]

        if len( children.value_expression ) == 2:
            # Without if
            return ListComprehensionNode( expression, name, min, max, position = position )

        condition = children.value_expression[ 2 ]

        # With if
        return ListComprehensionNode( expression, name, min, max, condition, position = position )


    def visit_expression ( self, node, children ):
        return children[ 0 ]

    def visit_value_expression ( self, node, children ):
        return children[ 0 ]

    def visit_binary_logic_operator_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        left = children.binary_comparison_operator_expression[ 0 ]
        right = children.binary_logic_operator_expression[ 0 ]

        op = children[ 1 ]

        if op == 'and':
            return AndLogicOperatorNode( left, right, position )
        elif op == 'or':
            return OrLogicOperatorNode( left, right, position )
        else:
            raise BaseException( "Unknown binary operator: %s" % op )
    
    def visit_binary_comparison_operator_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        left = children.binary_sum_operator_expression[ 0 ]
        right = children.binary_comparison_operator_expression[ 0 ]

        op = children[ 1 ]

        if op == '>=':
            return GreaterEqualComparisonOperatorNode( left, right, position )
        elif op == '>':
            return GreaterComparisonOperatorNode( left, right, position )
        elif op == '==':
            return EqualComparisonOperatorNode( left, right, position )
        elif op == '!=':
            return NotEqualComparisonOperatorNode( left, right, position )
        elif op == '<=':
            return LesserEqualComparisonOperatorNode( left, right, position )
        elif op == '<':
            return LesserComparisonOperatorNode( left, right, position )
        else:
            raise BaseException( "Unknown binary operator: %s" % op )

    def visit_binary_sum_operator_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        left = children.binary_mult_operator_expression[ 0 ]
        right = children.binary_sum_operator_expression[ 0 ]

        op = children[ 1 ]

        if op == '+':
            return PlusBinaryOperatorNode( left, right, position )
        elif op == '-':
            return MinusBinaryOperatorNode( left, right, position )
        else:
            raise BaseException( "Unknown binary operator: %s" % op )

    def visit_binary_mult_operator_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        left = children.unary_operator_expression[ 0 ]
        right = children.binary_mult_operator_expression[ 0 ]

        op = children[ 1 ]

        if op == '*':
            return MultBinaryOperatorNode( left, right, position )
        elif op == '/':
            return DivBinaryOperatorNode( left, right, position )
        else:
            raise BaseException( "Unknown binary operator: %s" % op )

    def visit_unary_operator_expression ( self, node, children ):
        if children[ 0 ] == '':
            return children.expression_single[ 0 ]

        position = ( node.position, node.position_end )

        return NotOperatorNode( children.expression_single[ 0 ], position =  position )

    def visit_expression_single ( self, node, children ):
        return children[ 0 ]

    def visit_music_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        return MusicParallelNode( list( children ), position = position )

    def visit_parallel ( self, node, children ):
        pass

    def visit_sequence ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        return MusicSequenceNode( list( children ), position )

    def visit_group ( self, node, children ):
        position = ( node.position, node.position_end )

        return GroupNode( children[ 0 ], position )

    def visit_block ( self, node, children ):
        position = ( node.position, node.position_end )

        return BlockNode( children.body[ 0 ], position )

    def visit_note ( self, node, children ):
        position = ( node.position, node.position_end )

        pitch_class = children.note_pitch[ 0 ][ 0 ]
        octave = children.note_pitch[ 0 ][ 1 ]
        accidental = children.note_accidental[ 0 ]
        value = Fraction( 1 )

        if len( children.note_value ) == 1:
            value = children.note_value[ 0 ]
         
        note = Note( 
            pitch_class = pitch_class,
            octave = octave,
            value = value,
            accidental = accidental
        )

        if len( children.chord_suffix ) == 1:
            chord = children.chord_suffix[ 0 ]

            return NoteNode( note, position ).as_chord( chord )
        else:
            return NoteNode( note, position )

    def visit_chord_suffix ( self, node, children ):
        if children[ 0 ] == 'M':
            return scales.major_chord
        elif children[ 0 ] == 'm':
            return scales.minor_chord
        else:
            return None

    def visit_variable ( self, node, children ):
        position = ( node.position, node.position_end )

        return VariableExpressionNode( children[ 0 ], position )

    def visit_function ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 2:
            return FunctionExpressionNode( children[ 0 ], children[ 1 ], position = position )
        
        return FunctionExpressionNode( children[ 0 ], position = position )

    def visit_function_parameters ( self, node, children ):
        return list( children )

    def visit_chord ( self, node, children ):
        position = ( node.position, node.position_end )

        return MusicParallelNode( list( children ), position )

    def visit_rest ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 1:
            return RestNode( value = children[ 0 ], position = position )

        return RestNode( position = position )

    def visit_note_accidental ( self, node, children ):
        if node.value == '^^':
            return NoteAccidental.DOUBLESHARP
        elif node.value == '^':
            return NoteAccidental.SHARP
        elif node.value == '_':
            return NoteAccidental.FLAT
        elif node.value == '__':
            return NoteAccidental.DOUBLEFLAT
        else:
            return NoteAccidental.NONE

    def visit_note_value ( self, node, children ):
        if len( children ) == 2:
            return children[ 0 ] / children[ 1 ]
        elif node.value.startswith( "/" ):
            return 1 / children[ 0 ]
        else:
            return children[ 0 ]

    def visit_note_pitch ( self, node, children ):
        return Note.parse_pitch_octave( ''.join( children ) )

    def visit_modifier ( self, node, children ):
        position = ( node.position, node.position_end )

        c = children[ 0 ].lower()
        
        if c == 't': return TempoModifierNode( children[ 1 ], position )
        elif c == 'v': return VelocityModifierNode( children[ 1 ], position )
        elif c == 'l': return LengthModifierNode( children[ 1 ], position )
        elif c == 's':
            if len( children ) == 3:
                return SignatureModifierNode( children[ 1 ], children[ 2 ], position )
            else:
                return SignatureModifierNode( lower = children[ 1 ], position = position )
        elif c == 'o': return OctaveModifierNode( children[ 1 ], position )

    def visit_instrument_modifier ( self, node, children ):
        position = ( node.position, node.position_end )

        return VoiceBlockModifier( children[ 1 ], children[ 0 ], position )

    # Strings
    def visit_string_value ( self, node, children ):
        position = ( node.position, node.position_end )

        return StringLiteralNode( children[ 0 ], position )

    def visit_double_string ( self, node, children ):
        return ''.join( children )

    def visit_double_string_char ( self, node, children ):
        if node.value == "\\\"":
            return "\""
        elif node.value == "\\\\":
            return "\\"
        else:
            return node.value

    def visit_single_string ( self, node, children ):
        return ''.join( children )

    def visit_single_string_char ( self, node, children ):
        if node.value == "\\'":
            return "'"
        elif node.value == "\\\\":
            return "\\"
        else:
            return node.value

    def visit_number_value ( self, node, children ):
        position = ( node.position, node.position_end )
        
        return NumberLiteralNode( children[ 0 ], position )

    def visit_bool_value ( self, node, children ):
        position = ( node.position, node.position_end )

        return BoolLiteralNode( children[ 0 ] == "true", position )

    def visit_none_value ( self, node, children ):
        position = ( node.position, node.position_end )

        return NoneLiteralNode( position )

    def visit_namespaced ( self, node, children ):
        return '\\'.join( children )

    def visit_identifier ( self, node, children ):
        return node.value
    
    def visit_alphanumeric ( self, node, children ):
        return node.value

    def visit_integer ( self, node, children ):
        return int( node.value )

    def visit_float ( self, node, children ):
        return float( node.value )

    def visit__ ( self, node, children ):
        return None

    def visit_e ( self, node, children ):
        return None

class Parser():
    def __init__ ( self ):
        self.debug : bool = False

        with open( Path( __file__ ).parent / "grammar.peg", "r" ) as f:
            self.internal_parser = ParserPEG( f.read(), "main", skipws=False, debug = False, memoization = True, comment_rule_name = "comment" )

    def parse ( self, expression ) -> Node:
        tree = self.internal_parser.parse( expression )
        
        result = visit_parse_tree( tree, ParserVisitor( debug = self.debug ) )
        
        return result

    def parse_file ( self, file ) -> Node:
        with open( file, 'r' ) as f:
            return self.parse( f.read() )