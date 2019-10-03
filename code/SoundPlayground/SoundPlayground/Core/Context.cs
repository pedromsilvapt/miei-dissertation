using System.Linq;

namespace SoundPlayground {
    public class Context {
        public (int, int) TimeSignature  { get; set; } = (4, 4);
        
        public int Channel { get; set; } = 0;

        public int Velocity { get; set; } = 120;

        public int Octave { get; set; } = 4;

        public float Value { get; set; } = 1 / 4f;

        public int Tempo { get; set; } = 120;

        public int Cursor { get; set; } = 0;

        public Context Fork () {
            return new Context {
                TimeSignature = TimeSignature,
                Channel = Channel,
                Velocity = Velocity,
                Octave = Octave,
                Value = Value,
                Tempo = Tempo,
                Cursor = Cursor
            };
        }

        public void Join ( params Context[] childContexts ) {
            Cursor = childContexts.Select( c => c.Cursor ).Max();
        }

        protected float GetDurationRatio () {
            float l = (float)TimeSignature.Item2;

            if ( TimeSignature.Item1 >= 6 && TimeSignature.Item1 % 3 == 0 ) {
                return 3 / l;
            } else {
                return 1 / l;
            }
        }

        public int GetDuration ( float value ) {
            float beatDuration = 60 / (float)Tempo;

            float wholeNoteDuration = beatDuration * 1000f / GetDurationRatio();

            return (int)( wholeNoteDuration * value );
        }
    }
}
