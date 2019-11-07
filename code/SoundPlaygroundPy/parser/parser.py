from arpeggio.peg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree
from core.events import NoteEvent, NoteAccidental
from .abstract_syntax_tree import Node
from .abstract_syntax_tree import NoteNode, MusicSequenceNode, MusicParallelNode
from .abstract_syntax_tree import RestNode, MusicRepeatNode, MusicGroupNode
from .abstract_syntax_tree.context_modifiers import LengthModifierNode, OctaveModifierNode, SignatureModifierNode, VelocityModifierNode, TempoModifierNode, InstrumentBlockModifier
from .abstract_syntax_tree.expressions import VariableExpressionNode, FunctionExpressionNode
from .abstract_syntax_tree.expressions import StringLiteralNode, NumberLiteralNode
from .abstract_syntax_tree.statements import StatementsListNode, InstrumentDeclarationStatementNode, VariableDeclarationStatementNode, FunctionDeclarationStatementNode
from .abstract_syntax_tree.statements import ForLoopStatementNode, WhileLoopStatementNode, IfStatementNode

class ParserVisitor(PTNodeVisitor):
    def visit_body ( self, node, children ):
        if len( children ) > 0 and children[ -1 ] == ";":
            children = children[:-1]

        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )

        return StatementsListNode( list( children ), position )

    def visit_statement ( self, node, children ):
        return children[ 0 ]

    def visit_var_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        return VariableDeclarationStatementNode( children[ 0 ], children[ 1 ], position )

    def visit_instrument_declaration ( self, node, children ):
        position = ( node.position, node.position_end )

        return InstrumentDeclarationStatementNode( children[ 0 ], children[ 1 ], position )
    
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
        return ForLoopStatementNode( children.namespaced[ 0 ], children.value_expression[ 0 ], children.value_expression[ 1 ], children.body[ 0 ] )

    def visit_expression ( self, node, children ):
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

    def visit_repeat ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        position = ( node.position, node.position_end )
    
        return MusicRepeatNode( children[ 0 ], children[ 1 ], position )

     
    def visit_expression_unambiguous ( self, node, children ):
        return children[ 0 ]

    def visit_group ( self, node, children ):
        position = ( node.position, node.position_end )

        return MusicGroupNode( children[ 0 ], position )

    def visit_note ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 3:
            return NoteNode( 
                pitch_class = children[ 1 ][ 0 ],
                octave = children[ 1 ][ 1 ],
                value = children[ 2 ],
                accidental = children[ 0 ],
                position = position
            )
        
        return NoteNode( 
            pitch_class = children[ 1 ][ 0 ], 
            octave = children[ 1 ][ 1 ], 
            accidental = children[ 0 ] ,
            position = position
        )

    def visit_variable ( self, node, children ):
        position = ( node.position, node.position_end )

        return VariableExpressionNode( children[ 0 ], position )

    def visit_function ( self, node, children ):
        position = ( node.position, node.position_end )

        if len( children ) == 2:
            return FunctionExpressionNode( children[ 0 ], children[ 1 ], position )
        
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
        return NoteNode.parse_pitch_octave( ''.join( children ) )

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

        return InstrumentBlockModifier( children[ 1 ], children[ 0 ], position )

    def visit_value_expression ( self, node, children ):
        return children[ 0 ]

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

    def visit_namespaced ( self, node, children ):
        return '\\'.join( children )

    def visit_alphanumeric ( self, node, children ):
        return node.value

    def visit_integer ( self, node, children ):
        return int( node.value )

    def visit_float ( self, node, children ):
        return float( node.value )

    def visit__ ( self, node, children ):
        return None

class Parser():
    def __init__ ( self ):
        with open( "parser/grammar.peg", "r" ) as f:
            self.internal_parser = ParserPEG( f.read(), "body", skipws=False )

    def parse ( self, expression ) -> Node:
        tree = self.internal_parser.parse( expression )

        return visit_parse_tree( tree, ParserVisitor( debug = False ) )

    def parse_file ( self, file ) -> Node:
        with open( file, 'r' ) as f:
            return self.parse( f.read() )
