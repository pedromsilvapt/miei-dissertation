from time import sleep
from typing import Optional
import bimpy
import asyncio
import time
import threading
from musikla.core import Context

class SingleWindow:
    def __init__ ( self, context : Context, title : str, render_fn, width : int = 600, height : int = 600, margin : int = 0, max_framerate : int = 60 ):
        self.context : Context = context
        self.title = title
        self.render_fn = render_fn
        self.width = width
        self.height = height
        self.margin = margin
        self.running : bool = False
        self.max_framerate : int = max_framerate
        self._opened = bimpy.Bool()
        self._bimpy_ctx = None

        self.start()

    def _render ( self, event : threading.Event = None ):
        ctx = self._bimpy_ctx

        with ctx:
            bimpy.set_next_window_pos(bimpy.Vec2(self.margin, self.margin), bimpy.Condition.Always)
            bimpy.set_next_window_size(bimpy.Vec2(ctx.width() - self.margin * 2, ctx.height() - self.margin * 2), bimpy.Condition.Always)

            if bimpy.begin(self.title, self._opened, bimpy.WindowFlags.NoTitleBar | bimpy.WindowFlags.NoResize):
                try:
                    self.render_fn()
                except BaseException as err:
                    self.context.script.print_error(err)

                bimpy.end()
            
            # We set the event so that the event loop is free before we call Render
            if event is not None:
                event.set()


    def _render_async ( self, loop : asyncio.AbstractEventLoop ):
        self._render()

        if not self._bimpy_ctx.should_close():
            loop.call_later(1 / self.max_framerate, self._render_async, loop)
        else:
            self.running = False
        
            self._bimpy_ctx = None
            self._opened = None

    def _block_thread ( self, event_start : threading.Event, event_stop : threading.Event ):
        event_start.set()

        event_stop.wait()
        event_stop.clear()

    def start(self):
        def _start_thread ( loop : asyncio.AbstractEventLoop ):
            event_start = threading.Event()
            event_stop = threading.Event()

            while not ctx.should_close():
                sleep(1.0 / self.max_framerate)
                loop.call_soon_threadsafe(self._block_thread, event_start, event_stop)
                event_start.wait()
                event_start.clear()

                self._render( event_stop )

            self.running = False
        
            self._bimpy_ctx = None
            self._opened = None

            # self._render_async( asyncio.get_event_loop() )
            
        self.running = True
        
        ctx = bimpy.Context()

        ctx.init(self.width, self.height, self.title)

        with ctx:
            bimpy.themes.set_light_theme()

        self._bimpy_ctx = ctx
        self._opened = bimpy.Bool()

        self._render_async( asyncio.get_event_loop() )

        # threading.Thread( target = _start, args = ( asyncio.get_event_loop(), ) ).start()
        
        
