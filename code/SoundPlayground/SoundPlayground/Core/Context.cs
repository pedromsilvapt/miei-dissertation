using System.Linq;

namespace SoundPlayground {
    public class Context {
        public (int, int) TimeSignature  { get; set; } = (4, 4);
        
        public int Octave { get; set; } = 4;

        public int Duration { get; set; } = 4;

        public int BPM { get; set; } = 120;

        public int Cursor { get; set; } = 0;

        public Context Fork () {
            return new Context { 
                Octave = Octave, 
                Duration = Duration,
                BPM = BPM,
                Cursor = Cursor 
            };
        }

        public void Join ( params Context[] childContexts ) {
            Cursor = childContexts.Select( c => c.Cursor ).Max();
        }

        public int CalculateDurationInMilliseconds ( int duration ) {
            float fullNoteLength = BPM * 1000 / 60f;

            return (int)( fullNoteLength / (float)duration );
        }
    }
}
