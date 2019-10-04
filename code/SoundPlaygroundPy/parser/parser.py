from arpeggio.peg import ParserPEG
from arpeggio import PTNodeVisitor, visit_parse_tree
from .abstract_syntax_tree import NoteNode, MusicSequenceNode, MusicParallelNode
from .abstract_syntax_tree import RestNode, MusicRepeatNode, MusicGroupNode
from .abstract_syntax_tree.context_modifiers import LengthModifierNode, OctaveModifierNode, SignatureModifierNode, VelocityModifierNode, TempoModifierNode, InstrumentBlockModifier


class ParserVisitor(PTNodeVisitor):
    def visit_body ( self, node, children ):
        return children[ 0 ]

    def visit_expression ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        return MusicParallelNode( children )

    def visit_parallel ( self, node, children ):
        pass

    def visit_sequence ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]

        return MusicSequenceNode( children )

    def visit_repeat ( self, node, children ):
        if len( children ) == 1:
            return children[ 0 ]
    
        return MusicRepeatNode( children[ 0 ], children[ 1 ] )

     
    def visit_expression_unambiguous ( self, node, children ):
        return children[ 0 ]

    def visit_group ( self, node, children ):
        return MusicGroupNode( children[ 0 ] )

    def visit_note ( self, node, children ):
        if len( children ) == 2:
            return NoteNode( 
                pitch_class = children[ 0 ][ 0 ],
                octave = children[ 0 ][ 1 ],
                value = children[ 1 ]
            )
        
        return NoteNode( pitch_class = children[ 0 ] )

    def visit_chord ( self, node, children ):
        return MusicParallelNode( children )

    def visit_rest ( self, node, children ):
        if len( children ) == 1:
            return RestNode( value = children[ 0 ] )

        return RestNode()

    def visit_note_value ( self, node, children ):
        if len( children ) == 2:
            return children[ 0 ] / children[ 1 ]
        elif node.value.startswith( "/" ):
            return 1 / children[ 0 ]
        else:
            return children[ 0 ]

    def visit_note_pitch ( self, node, children ):
        return NoteNode.parse_pitch_octave( node.value )

    def visit_modifier ( self, node, children ):
        c = node.value[ 0 ].lower()
        
        if c == 't': return TempoModifierNode( children[ 0 ] )
        elif c == 'v': return VelocityModifierNode( children[ 0 ] )
        elif c == 'l': return LengthModifierNode( children[ 0 ] )
        elif c == 's': 
            if len( children ) == 2:
                return SignatureModifierNode( children[ 0 ], children[ 1 ] )
            else:
                return SignatureModifierNode( lower = children[ 0 ] )
        elif c == 'o': return OctaveModifierNode( children[ 0 ] )

    def visit_instrument_modifier ( self, node, children ):
        return InstrumentBlockModifier( children[ 1 ], children[ 0 ] )

    def visit_alphanumeric ( self, node, children ):
        return node.value

    def visit_integer ( self, node, children ):
        return int( node.value )

class Parser():
    def __init__ ( self ):
        with open( "parser/grammar.peg", "r" ) as f:
            self.internal_parser = ParserPEG( f.read(), "body" )

    def parse ( self, expression ):
        tree = self.internal_parser.parse( expression )

        return visit_parse_tree( tree, ParserVisitor( debug = False ) )