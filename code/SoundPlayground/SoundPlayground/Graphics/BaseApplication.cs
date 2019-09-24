using ImGuiNET;
using System;
using System.Collections.Generic;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;
using Veldrid;
using Veldrid.Sdl2;
using Veldrid.StartupUtilities;

namespace SoundPlayground.Graphics
{
    public class BaseApplication
    {
        protected Sdl2Window _window;
        protected GraphicsDevice _gd;
        protected CommandList _cl;
        protected ImGuiController _controller;

        protected string title = "ImGui.NET Sample Program";
        protected int framerate = 75;
        protected Vector3 _clearColor = new Vector3(0.45f, 0.55f, 0.6f);

        protected Queue<Func<Task>> tasks = new Queue<Func<Task>>();

        public BaseApplication()
        {
            // Create window, GraphicsDevice, and all resources necessary for the demo.
            VeldridStartup.CreateWindowAndGraphicsDevice(
                new WindowCreateInfo(50, 50, 1480, 920, WindowState.Maximized, this.title),
                new GraphicsDeviceOptions(true, null, true),
                GraphicsBackend.OpenGL,
                out _window,
                out _gd);
            _window.Resized += () =>
            {
                _gd.MainSwapchain.Resize((uint)_window.Width, (uint)_window.Height);
                _controller.WindowResized(_window.Width, _window.Height);
            };
            _cl = _gd.ResourceFactory.CreateCommandList();
            _controller = new ImGuiController(_gd, _gd.MainSwapchain.Framebuffer.OutputDescription, _window.Width, _window.Height);
        }

        public ImGuiController Controller { get => this._controller; }

        public async Task<(int, int)> CapFramerate(int minFrameTime, int? lastTime = null)
        {
            int currentTime = Environment.TickCount;

            if (lastTime != null)
            {
                int delta = currentTime - lastTime.Value;

                await Task.Delay(Math.Max(minFrameTime - delta - 1, 0));

                currentTime = Environment.TickCount;

                return (currentTime, currentTime - lastTime.Value);
            }

            return (currentTime, minFrameTime);
        }

        public void Async(Func<Task> func)
        {
            Task task = func();

            if (task.Status == TaskStatus.Created)
            {
                task.Start();
            }

            task.ContinueWith(res =>
            {
                if (res.IsFaulted)
                {
                    Console.WriteLine(res.Exception.InnerException.Message);
                    Console.WriteLine(res.Exception.InnerException.StackTrace);
                }
            });
        }

        public void Async(Func<Task<object>> func)
        {
            Async(async () =>
            {
                await func();
            });
        }

        #pragma warning disable CS1998
        public void Defer(Action task) => Defer(async () => task());
        #pragma warning restore CS1998 
        public void Defer(Func<Task<object>> task) => Defer(async () =>
        {
            await task();
        });
        public void Defer(Func<Task> task)
        {
            tasks.Enqueue(task);
        }

        #pragma warning disable CS1998
        public virtual async Task Load() { }

        public virtual async Task Unload() { }
        #pragma warning restore CS1998

        public async Task Run()
        {
            await this.Load();

            int minFrameTime = 1000 / this.framerate;

            var (lastTime, delta) = await CapFramerate(minFrameTime);

            while (_window.Exists)
            {
                InputSnapshot snapshot = _window.PumpEvents();
                if (!_window.Exists) { break; }

                (lastTime, delta) = await CapFramerate(minFrameTime, lastTime);


                _controller.Update(delta / 1000f, snapshot); // Feed the input events to our ImGui controller, which passes them through to ImGui.

                this.Render();

                _cl.Begin();
                _cl.SetFramebuffer(_gd.MainSwapchain.Framebuffer);
                _cl.ClearColorTarget(0, new RgbaFloat(_clearColor.X, _clearColor.Y, _clearColor.Z, 1f));
                _controller.Render(_gd, _cl);
                _cl.End();
                _gd.SubmitCommands(_cl);
                _gd.SwapBuffers(_gd.MainSwapchain);

                while (tasks.TryDequeue(out Func<Task> task))
                {
                    await task();
                }
            }

            await this.Unload();

            _gd.WaitForIdle();
            _controller.Dispose();
            _cl.Dispose();
            _gd.Dispose();
        }

        public void Main()
        {
            AsyncPump.Run(this.Run);
        }

        public virtual void Render() { }

        public void Quit()
        {
            this._window.Close();
        }
    }
}
