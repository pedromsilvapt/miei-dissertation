#!/usr/bin/python3
from core import Context, Instrument
from parser.abstract_syntax_tree import MusicSequenceNode
from parser.abstract_syntax_tree.context_modifiers import ContextModifierNode
from graphics import BaseApplication
from parser import Parser
from audio.midi_player import MidiPlayer
import imgui

class Application( BaseApplication ):
    def __init__ ( self ):
        self.code = """S6/8 T70 L/8 V70
(
    (A/8*11 G/8 F/8*12 | A,6/8 A,5/8 G,/8 F,6/8*2)*3
  | (r3 L3/8 a c' d' e'9/8 r9/8 e' d' c' a9/8)
)"""

        self.parsedTree = None

    def create_context ( self, ):
        return Context(
            time_signature = (6, 8),
            tempo = 75,
            velocity = 127,
            instruments = {
                'piano': Instrument( 'piano', 0, 0, 1 ),
                'violin': Instrument( 'violin', 1, 1, 1 )
            }
        )
    
    def render ( self ):
        super().render()

        if imgui.begin( "Music Editor" ):
            ( width, height ) = imgui.get_content_region_available();

            ( changed, value ) = imgui.input_text_multiline( "###Code", self.code, 1000, width = width, height = height / 2 )
            if changed: self.code = value
            
            if imgui.button( "Parse" ):
                self.parsedTree = Parser().parse( self.code )

                self.player = MidiPlayer( self.parsedTree.get_events( self.create_context() ) ).play()

            imgui.begin_child( "inspector", 0, 0, border = True )
            if self.parsedTree != None:
                self.render_inspector( self.parsedTree )
            imgui.end_child()

            imgui.end()

    def render_inspector ( self, obj, prefix = None ):
        properties = obj.__dict__

        node_name = f"{obj.__class__.__name__}###{id( obj )}";

        if imgui.tree_node( node_name if prefix != None else f"{prefix}: {node_name}", imgui.TREE_NODE_DEFAULT_OPEN ):
            for key,value in properties.items():
                self.render_inspector_value( key, value );

            imgui.tree_pop()

    def render_inspector_value ( self, key, value ):
        if isinstance( value, int )\
        or isinstance( value, bool )\
        or isinstance( value, float )\
        or isinstance( value, str )\
        or isinstance( value, tuple )\
        or value is None:
            imgui.bullet_text( f"{key}: {value}" )
        elif isinstance( value, list ):
            if imgui.tree_node( f"{ key }: { value.__class__.__name__ }({ len( value ) } items)###{ id( value ) }", imgui.TREE_NODE_DEFAULT_OPEN ):
                i = 0;

                for obj in value:
                    self.render_inspector_value( str( i ), obj );

                    i += 1

                imgui.tree_pop()
        else:
            self.render_inspector( value, key )

if __name__ == "__main__":
    Application().run()
