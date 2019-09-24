namespace SoundPlayground
{
    class Program
    {
        static void Main(string[] args)
        {
            // Main code is in the Application.Render()
			Graphics.AsyncPump.Run( () => new Application().Run() );
        }
    }
}
