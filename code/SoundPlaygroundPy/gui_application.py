from core import Context, Instrument, VALUE_KIND_MUSIC
from parser.abstract_syntax_tree import MusicSequenceNode
from parser.abstract_syntax_tree.context_modifiers import ContextModifierNode
from graphics import BaseApplication
from libraries import KeyboardLibrary, KeyStroke, StandardLibrary
from parser import Parser
from audio import MidiPlayer
from audio.sequencers import FluidSynthSequencer
import imgui
import glfw
import traceback

EXPRESSION_TAB_AST = 0
EXPRESSION_TAB_EVENTS = 1
EXPRESSION_TAB_KEYBOARD = 2

class GuiApplication( BaseApplication ):
    def __init__ ( self ):
        with open( 'examples/westworld.ml', 'r' ) as f:
            self.code = f.read()



#         self.code = """S4/4 T74 L/8 V120;

# register_key( "a"; A,, E, A, B, C B, A, E, D, F, C E C A, );
# """

        self.parsedTree = None
        self.parsedException = None
        self.player = None
        self.context = None

        self.expressionTab = EXPRESSION_TAB_AST

    def create_context ( self, ):
        ctx = Context(
            time_signature = (6, 8),
            tempo = 75,
            velocity = 127,
            instruments = [
                Instrument( 'piano', 0, 0, 1 )
                # Instrument( 'violin', 41, 1, 1 )
            ]
        )

        ctx.link( StandardLibrary() )
        ctx.link( KeyboardLibrary() )

        return ctx
    
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

    def render_inspector_events ( self ):
        imgui.begin_child( "notes", 0, 0, border = True )
        if self.player != None:
            for note in self.player.events:
                imgui.text( str( note ) )
        imgui.end_child()

    def get_pressed_keystrokes ( self ):
        for i in range( glfw.KEY_A, glfw.KEY_Z + 1 ):
            if imgui.get_io().keys_down[ i ]:
                yield KeyStroke( 
                    imgui.get_io().key_ctrl, 
                    imgui.get_io().key_alt, 
                    imgui.get_io().key_shift, 
                    chr( ord( 'a' ) + ( i - glfw.KEY_A ) )
                )

    def render_inspector_keyboard ( self ):
        imgui.begin_child( "keyboard", 0, 0, border = True )

        if self.context != None:
            current_keys = self.get_pressed_keystrokes()

            pressed = set()

            keyboard = self.context.library( KeyboardLibrary )

            for key, events in keyboard.trigger_keys( set( current_keys ) ):
                pressed.add( key )

                if events != None and events.kind == VALUE_KIND_MUSIC:
                    self.player.play_more( events )


            for key, expr in keyboard.registered_keys():
                is_pressed = key in pressed

                imgui.bullet()

                if is_pressed: imgui.text_colored( str( key ), 0, 1, 0 )
                else: imgui.text( str( key ) )

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

            try:
                if to_parse or to_play:
                    self.parsedTree = Parser().parse( self.code )

                    self.context = self.create_context()

                    self.player = MidiPlayer( events = list( self.parsedTree.eval( self.context ) ) )
                    self.player.sequencers.append( FluidSynthSequencer() )

                    self.parsedException = None
                
                if to_play:
                    self.player.play()
            except Exception as ex:
                self.parsedException = ex
                print(ex)
                traceback.print_tb(ex.__traceback__)

            if self.parsedException != None:
                imgui.text_colored( str( self.parsedException ), 1, 0, 0 )

            
            self.expressionTab = self.imgui_tabbar( self.expressionTab, [
                ( EXPRESSION_TAB_AST, "AST", self.render_inspector_ast ),
                ( EXPRESSION_TAB_EVENTS, "Events", self.render_inspector_events ),
                ( EXPRESSION_TAB_KEYBOARD, "Keyboard", self.render_inspector_keyboard )
            ] )

            imgui.end()

    def render_inspector ( self, obj, prefix = None ):
        properties = obj.__dict__

        node_name = f"{obj.__class__.__name__}###{id( obj )}";

        if imgui.tree_node( node_name if prefix != None else f"{prefix}: {node_name}", imgui.TREE_NODE_DEFAULT_OPEN ):
            for key, value in properties.items():
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
