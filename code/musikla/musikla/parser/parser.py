from pathlib import Path
from arpeggio.peg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree
from typing import Any, List, cast
from musikla.core.events import NoteEvent
from musikla.core.theory import NoteAccidental, Note, Chord
from .abstract_syntax_tree import Node, PythonNode
from .abstract_syntax_tree import NoteNode, ChordNode, MusicSequenceNode, MusicParallelNode, RestNode
from .abstract_syntax_tree.context_modifiers import LengthModifierNode, OctaveModifierNode, SignatureModifierNode, VelocityModifierNode, InstrumentModifierNode, TempoModifierNode, VoiceBlockModifier

from .abstract_syntax_tree.expressions import VariableExpressionNode, FunctionExpressionNode, ListComprehensionNode
from .abstract_syntax_tree.expressions import StringLiteralNode, NumberLiteralNode, BoolLiteralNode, NoneLiteralNode
from .abstract_syntax_tree.expressions import ObjectLiteralNode, ArrayLiteralNode

from .abstract_syntax_tree.expressions import PlusBinaryOperatorNode, MinusBinaryOperatorNode, PowBinaryOperatorNode, MultBinaryOperatorNode, DivBinaryOperatorNode
from .abstract_syntax_tree.expressions import AndLogicOperatorNode, OrLogicOperatorNode

from .abstract_syntax_tree.expressions import GreaterComparisonOperatorNode, GreaterEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import EqualComparisonOperatorNode, NotEqualComparisonOperatorNode
from .abstract_syntax_tree.expressions import LesserComparisonOperatorNode, LesserEqualComparisonOperatorNode

from .abstract_syntax_tree.expressions import NotOperatorNode, GroupNode, BlockNode, PropertyAccessorNode

from .abstract_syntax_tree.statements import StatementsListNode, VariableDeclarationStatementNode, FunctionDeclarationStatementNode
from .abstract_syntax_tree.statements import ForLoopStatementNode, WhileLoopStatementNode, IfStatementNode, ReturnStatementNode, ImportStatementNode

from .abstract_syntax_tree.macros import KeyboardDeclarationMacroNode, KeyboardShortcutMacroNode, KeyboardShortcutDynamicMacroNode, KeyboardShortcutComprehensionMacroNode, KeyboardForLoopMacroNode, KeyboardWhileLoopMacroNode, KeyboardIfMacroNode, KeyboardBlockMacroNode
from .abstract_syntax_tree.macros import VoiceDeclarationMacroNode

from fractions import Fraction

class ParserVisitor(PTNodeVisitor):
    def visit_body ( self, node, children ):
        children = children.statement
        
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        children = list( children )

        if any( ( c.hoisted for c in children ) ):
            children = [
                *filter( lambda c: c.hoisted, children ),
                *filter( lambda c: not c.hoisted, children )
            ]

        return StatementsListNode( children, position = position )

    def visit_comment ( self, node, children ):
        return None

    def visit_statement ( self, node, children ):
        return children[ 0 ]

    def visit_import ( self, node, children ):
        position = ( node.position, node.position_end )

        if children.namespaced:
            return ImportStatementNode( children.namespaced[ 0 ], False, position = position )

        return ImportStatementNode( children.string_value[ 0 ].value, True, position = position )

    def visit_var_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        operator = children.var_declaration_infix[ 0 ] if children.var_declaration_infix else None

        return VariableDeclarationStatementNode( children.namespaced[ 0 ], children.expression[ 0 ], operator = operator, position = position )

    def visit_var_declaration_infix ( self, node, children ):
        if not children:
            return None

        return children[ 0 ]

    def visit_voice_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        name = children.namespaced[ 0 ]
        args = children.voice_declaration_body[ 0 ]
        
        return VoiceDeclarationMacroNode( 
            name, args[ 0 ], args[ 1 ],
            position = position
        )
    
    def visit_voice_declaration_body ( self, node, children ):
        modifiers = children.expression[ 0 ]
        parent = None

        if children.namespaced:
            parent = VariableExpressionNode( children.namespaced[ 0 ] ) 

        return ( modifiers, parent )

    def visit_function_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        name = children.namespaced[ 0 ] if children.namespaced else None

        body = children.body[ 0 ] if children.body else StatementsListNode( [ children.expression[ 0 ] ] )

        if children.arguments:
            return FunctionDeclarationStatementNode( name, children.arguments[ 0 ], body, position )

        return FunctionDeclarationStatementNode( name, [], body, position )
    
    def visit_arguments ( self, node, children ):
        return list( children.single_argument )
    
    def visit_single_argument ( self, node, children ):
        prefix = children.single_argument_prefix[ 0 ] if children.single_argument_prefix else None
        identifier = children.identifier[ 0 ]

        if children.expression:
            return ( identifier, prefix, children.expression[ 0 ] )

        return ( identifier, prefix, None )

    def visit_single_argument_prefix ( self, node, children ):
        return children[ 0 ] or None

    def visit_for_variables ( self, node, children ):
        return list( [ v.name for v in children.variable ] )

    def visit_for_loop_head ( self, node, children ):
        if len( children.value_expression ) == 1:
            expression = children.value_expression[ 0 ]
        else:
            expression = FunctionExpressionNode( VariableExpressionNode( "range" ), [ children.value_expression[ 0 ], children.value_expression[ 1 ] ] )
        
        return ( children.for_variables[ 0 ], expression )
            

    def visit_for_loop_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        variables, expression = children.for_loop_head[ 0 ]

        return ForLoopStatementNode( variables, expression, children.body[ 0 ], position )

    def visit_while_loop_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        return WhileLoopStatementNode( children.expression[ 0 ], children.body[ 0 ], position )
    
    def visit_if_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children.body ) == 2:
            return IfStatementNode( children.expression[ 0 ], children.body[ 0 ], children.body[ 1 ], position )

        return IfStatementNode( children.expression[ 0 ], children.body[ 0 ], position = position )

    def visit_return_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        if children.expression:
            return ReturnStatementNode( children.expression[ 0 ], position = position )

        return ReturnStatementNode( position = position )

    def visit_keyboard_declaration ( self, node, children ):
        if len( children.group ):
            return KeyboardDeclarationMacroNode( children.keyboard_body[ 0 ], list( children.alphanumeric ), children.group[ 0 ].expression )

        return KeyboardDeclarationMacroNode( children.keyboard_body[ 0 ], list( children.alphanumeric ) )

    def visit_keyboard_body ( self, node, children ):
        return list( children.keyboard_body_statement )

    def visit_keyboard_body_statement ( self, node, children ):
        return children[ 0 ]

    def visit_keyboard_for ( self, node, children ):
        position = ( node.position, node.position_end )
        
        var_name, expression = children.for_loop_head[ 0 ]

        return KeyboardForLoopMacroNode( var_name, expression, children.keyboard_body[ 0 ], position = position )
    
    def visit_keyboard_while ( self, node, children ):
        position = ( node.position, node.position_end )

        return KeyboardWhileLoopMacroNode( children.expression[ 0 ], children.keyboard_body[ 0 ], position = position )
    
    def visit_keyboard_if ( self, node, children ):
        position = ( node.position, node.position_end )
        
        else_body = children.keyboard_body[ 1 ] if len( children.keyboard_body ) > 1 else None

        return KeyboardIfMacroNode( children.expression[ 0 ], children.keyboard_body[ 0 ], else_body, position = position )
    
    def visit_keyboard_block ( self, node, children ):
        position = ( node.position, node.position_end )
        
        return KeyboardBlockMacroNode( children.body[ 0 ], position = position )

    def visit_keyboard_shortcut ( self, node, children ):
        position = ( node.position, node.position_end )

        kind, key, flags = children.keyboard_shortcut_key[ 0 ]

        expr = children.expression[ 0 ]

        args = children.keyboard_arguments[ 0 ] if children.keyboard_arguments else []

        if kind == KeyboardShortcutComprehensionMacroNode:
            return KeyboardShortcutComprehensionMacroNode( key, flags, args, expr, position )
        elif kind == KeyboardShortcutDynamicMacroNode:
            return KeyboardShortcutDynamicMacroNode( key, flags, args, expr, position )
        else:
            return KeyboardShortcutMacroNode( key, args, expr, position )

    def visit_keyboard_shortcut_key ( self, node, children ):
        if len( children.list_comprehension ) == 1:
            return ( 
                KeyboardShortcutComprehensionMacroNode, 
                children.list_comprehension[ 0 ],
                list( children.alphanumeric )
            )
        elif len( children.value_expression ) == 1 or len( children.string_value ) == 1:
            if children.string_value:
                variable = children.string_value[ 0 ]
            else:
                variable = children.value_expression[ 0 ]

            return (
                KeyboardShortcutDynamicMacroNode,
                variable,
                list( children.alphanumeric )
            )
        else:
            return (
                KeyboardShortcutMacroNode,
                list( children.alphanumeric ),
                None
            )

    def visit_list_comprehension ( self, node, children ):
        position = ( node.position, node.position_end )

        expression = children.expression[ 0 ]
        name = [ children.namespaced[ 0 ] ]
        min = children.value_expression[ 0 ]
        max = children.value_expression[ 1 ]

        if len( children.value_expression ) == 2:
            # Without if
            return ListComprehensionNode( expression, name, min, max, position = position )

        condition = children.value_expression[ 2 ]

        # With if
        return ListComprehensionNode( expression, name, min, max, condition, position = position )

    def visit_keyboard_arguments ( self, node, children ):
        if children.keyboard_single_argument:
            return list( children.keyboard_single_argument )
        
        return []

    def visit_keyboard_single_argument ( self, node, children ):
        return children.identifier[ 0 ]

    def visit_python_expression ( self, node, children ):
        position = ( node.position, node.position_end )

        return PythonNode( children.python_expression_body[ 0 ], True, position = position )

    def visit_python_expression_body ( self, node, children ):
        return node.value

    def visit_python_statement ( self, node, children ):
        position = ( node.position, node.position_end )

        return PythonNode( children.python_statement_body[ 0 ], False, position = position )

    def visit_python_statement_body ( self, node, children ):
        return ''.join( children )

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

        if op == '**':
            return PowBinaryOperatorNode( left, right, position )
        elif op == '*':
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
        expression = children[ 0 ]

        accessors = children[ 1: ]

        if accessors:
            accessors[ 0 ].expression = expression

            for i in range( 1, len( accessors ) ):
                accessors[ i ].expression = accessors[ i - 1 ]
            
            expression = accessors[ -1 ]

        return expression

    def visit_expression_single_prefix ( self, node, children ):
        return children[ 0 ]

    def visit_property_accessor ( self, node, children ):
        identifier = None

        if children.identifier:
            position = ( node.position, node.position_end )

            identifier = StringLiteralNode( children.identifier[ 0 ], position = position )
        else:
            identifier = children.expression[ 0 ]

        position = ( node.position, node.position_end )

        return PropertyAccessorNode( cast( Any, None ), identifier, position = position )
        
    def visit_property_call ( self, node, children ):
        position = ( node.position, node.position_end )

        parameters = children.function_parameters[ 0 ]
        
        return FunctionExpressionNode( None, parameters[ 0 ], parameters[ 1 ], position = position )

    def visit_array_value ( self, node, children ):
        position = ( node.position, node.position_end )

        if children.expression:
            return ArrayLiteralNode( list( children.expression ), position )
        
        return ArrayLiteralNode( [], position )
    
    def visit_object_value ( self, node, children ):
        position = ( node.position, node.position_end )
        
        if children.object_value_item:
            return ObjectLiteralNode( list( children.object_value_item ), position )
        
        return ObjectLiteralNode( [], position )

    def visit_object_value_item ( self, node, children ):
        return ( children.object_value_key[ 0 ], children.expression[ 0 ] )

    def visit_object_value_key ( self, node, children ):
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

    def visit_variable ( self, node, children ):
        position = ( node.position, node.position_end )

        return VariableExpressionNode( children[ 0 ], position )

    def visit_function ( self, node, children ):
        position = ( node.position, node.position_end )

        parameters = children.function_parameters[ 0 ]
        
        name = children.namespaced[ 0 ]

        return FunctionExpressionNode( VariableExpressionNode( name ), parameters[ 0 ], parameters[ 1 ], position = position )

    def visit_function_parameters ( self, node, children ):
        if children.positional_parameters:
            if children.named_parameters:
                return ( children.positional_parameters[ 0 ], children.named_parameters[ 0 ] )
            else:
                return ( children.positional_parameters[ 0 ], {} )
        elif children.named_parameters:
            return ( [], children.named_parameters[ 0 ] )
        else:
            return ( [], {} )

    def visit_positional_parameters ( self, node, children ):
        return list( children.expression )
    
    def visit_named_parameters ( self, node, children ):
        return dict( children.named_parameter )

    def visit_named_parameter ( self, node, children ):
        return ( children.identifier[ 0 ], children.expression[ 0 ] )

    def visit_note ( self, node, children ):
        position = ( node.position, node.position_end )

        accidental, ( pitch_class, octave ) = children.note_pitch[ 0 ]
        
        value = Fraction( 1 )

        if children.note_value:
            value = children.note_value[ 0 ]
         
        note = Note( 
            pitch_class = pitch_class,
            octave = octave,
            value = value,
            accidental = accidental
        )

        return NoteNode( note, position )

    def visit_chord ( self, node, children ):
        position = ( node.position, node.position_end )
        
        value = Fraction( 1 )

        if children.note_value:
            value = children.note_value[ 0 ]

        if children.chord_suffix:
            accidental, ( pitch_class, octave ) = children.note_pitch[ 0 ]

            chord = children.chord_suffix[ 0 ]

            note = Note( 
                pitch_class = pitch_class,
                octave = octave,
                value = value,
                accidental = accidental
            )

            return ChordNode( Chord.from_abbreviature( note, chord, value ), position = position )
        else:
            notes : List[Note] = []

            for accidental, ( pitch_class, octave ) in children.note_pitch:
                notes.append( Note( 
                    pitch_class = pitch_class,
                    octave = octave,
                    value = value,
                    accidental = accidental
                ) )

            return ChordNode( Chord( notes, None, value ), position = position )

    def visit_chord_suffix ( self, node, children ):
        return children[ 0 ]

    def visit_rest ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 1:
            return RestNode( value = children[ 0 ], visible = True, position = position )

        return RestNode( visible = True, position = position )

    def visit_note_value ( self, node, children ):
        if len( children ) == 2:
            return children[ 0 ] / children[ 1 ]
        elif node.value.startswith( "/" ):
            return 1 / children[ 0 ]
        else:
            return children[ 0 ]

    def visit_note_pitch ( self, node, children ):
        return ( children.note_accidental[ 0 ], children.note_pitch_raw[ 0 ] )

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

    def visit_note_pitch_raw ( self, node, children ):
        return Note.parse_pitch_octave( ''.join( children ) )

    def visit_modifier ( self, node, children ):
        position = ( node.position, node.position_end )

        c = children[ 0 ].lower()
        
        if c == 't': return TempoModifierNode( children[ 1 ], position )
        elif c == 'v': return VelocityModifierNode( children[ 1 ], position )
        elif c == 'i': return InstrumentModifierNode( children[ 1 ], position )
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
