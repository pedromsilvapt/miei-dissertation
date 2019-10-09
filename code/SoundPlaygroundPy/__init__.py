#!/usr/bin/python3
from core import Context, Instrument
from parser.abstract_syntax_tree import MusicSequenceNode
from parser.abstract_syntax_tree.context_modifiers import ContextModifierNode
from graphics import BaseApplication
from parser import Parser
from audio.midi_player import MidiPlayer
import imgui

EXPRESSION_TAB_AST = 0
EXPRESSION_TAB_NOTES = 1
EXPRESSION_TAB_COMMANDS = 2

class Application( BaseApplication ):
    def __init__ ( self ):
        self.code = """S6/8 T70 L/8 V70
(
    (A/8*11 G/8 F/8*12 | A,6/8 A,5/8 G,/8 F,6/8*2)*3
  | (r3 L3/8 (:violin a c' d' e'9/8) r9/8 e' d' c' a9/8)
)"""

        self.parsedTree = None

        self.expressionTab = EXPRESSION_TAB_AST

    def create_context ( self, ):
        return Context(
            time_signature = (6, 8),
            tempo = 75,
            velocity = 127,
            instruments = {
                'piano': Instrument( 'piano', 0, 0, 1 ),
                'violin': Instrument( 'violin', 41, 1, 1 )
            }
        )
    
    def imgui_tabbar ( self, open_tab, tabs ):
        width = imgui.get_content_region_available_width()

        tab_width = ( width - imgui.get_style().item_spacing.x * ( len( tabs ) - 1 ) ) / len( tabs )

        first = True

        open_panel = None

        for key, label, panel in tabs:
            if not first: 
                imgui.same_line()

            if imgui.button( label, width = tab_width ):
                open_tab = key

            if open_tab == key:
                open_panel = panel

            first = False

        if open_panel != None:
            open_panel()

        return open_tab
        
    def render_inspector_ast ( self ):
        imgui.begin_child( "inspector", 0, 0, border = True )
        if self.parsedTree != None:
            self.render_inspector( self.parsedTree )
        imgui.end_child()

    def render_inspector_notes ( self ):
        imgui.begin_child( "notes", 0, 0, border = True )
        if self.player != None:
            for note in self.player.notes:
                imgui.text( str( note ) )
        imgui.end_child()
    
    def render_inspector_commands ( self ):
        imgui.begin_child( "commands", 0, 0, border = True )
        if self.player != None:
            for command in self.player.commands:
                imgui.text( str( command ) )
        imgui.end_child()

    def render ( self ):
        super().render()

        if imgui.begin( "Music Editor" ):
            ( width, height ) = imgui.get_content_region_available();

            ( changed, value ) = imgui.input_text_multiline( "###Code", self.code, 1000, width = width, height = height / 2 )
            if changed: self.code = value
            
            to_parse = False
            to_play = False

            if imgui.button( "Parse" ):
                to_parse = True

            imgui.same_line()
            
            if imgui.button( "Play" ):
                to_play = True

            if to_parse or to_play:
                self.parsedTree = Parser().parse( self.code )

                self.player = MidiPlayer( list( self.parsedTree.get_events( self.create_context() ) ) )
            
            if to_play:
                self.player.play()

            self.expressionTab = self.imgui_tabbar( self.expressionTab, [
                ( EXPRESSION_TAB_AST, "AST", self.render_inspector_ast ),
                ( EXPRESSION_TAB_NOTES, "Notes", self.render_inspector_notes ),
                ( EXPRESSION_TAB_COMMANDS, "Commands", self.render_inspector_commands )
            ] )

            # if imgui.button( "AST" ): self.expressionTab = EXPRESSION_TAB_AST
            # imgui.same_line()
            # if imgui.button( "Notes" ): self.expressionTab = EXPRESSION_TAB_NOTES
            # imgui.same_line()
            # if imgui.button( "Commands" ): self.expressionTab = EXPRESSION_TAB_COMMANDS

            # if self.expressionTab == EXPRESSION_TAB_AST:
                
            # elif self.expressionTab == EXPRESSION_TAB_NOTES:
            #     imgui.begin_child( "inspector", 0, 0, border = True )
            #     if self.parsedTree != None:
            #         self.render_inspector( self.parsedTree )
            #     imgui.end_child()
            # elif self.expressionTab == EXPRESSION_TAB_COMMANDS:
            #     imgui.begin_child( "inspector", 0, 0, border = True )
            #     if self.parsedTree != None:
            #         self.render_inspector( self.parsedTree )
            #     imgui.end_child()

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
