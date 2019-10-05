import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer

class BaseApplication():
    def impl_glfw_init( self ):
        width, height = 1280, 720
        window_name = "Music Language"

        if not glfw.init():
            print("Could not initialize OpenGL context")
            exit(1)

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(
            int(width), int(height), window_name, None, None
        )
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            exit(1)

        return window

    def render ( self ):
        pass

    def run ( self ):
        imgui.create_context()
        window = self.impl_glfw_init()
        impl = GlfwRenderer( window )

        while not glfw.window_should_close( window ):
            glfw.poll_events()
            impl.process_inputs()

            imgui.new_frame()

            self.render()

            gl.glClearColor( 1., 1., 1., 1 )
            gl.glClear( gl.GL_COLOR_BUFFER_BIT )

            imgui.render()
            impl.render( imgui.get_draw_data() )
            glfw.swap_buffers( window )

        impl.shutdown()
        glfw.terminate()
