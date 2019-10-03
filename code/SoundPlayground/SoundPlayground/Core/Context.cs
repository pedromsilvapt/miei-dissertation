using System.Collections.Generic;
using System.Linq;
using SoundPlayground.Core;

namespace SoundPlayground {
    public class Context {
        public SharedContext Shared { get;set; } = new SharedContext();

        public (int, int) TimeSignature  { get; set; } = ( 4, 4 );
        
        public int Channel { get; set; } = 0;

        public int Velocity { get; set; } = 120;

        public int Octave { get; set; } = 4;

        public float Value { get; set; } = 1 / 4f;

        public int Tempo { get; set; } = 120;

        public int Cursor { get; set; } = 0;

        public Dictionary<string, Instrument> Instruments { get; set; } = new Dictionary<string, Instrument>();

        public Instrument AddInstrument ( string name, int program ) {
            Instrument instrument = new Instrument( name, program, null );

            Instruments[ name ] = instrument;

            return instrument;
        }

        public Context Fork () {
            return new Context {
                Shared = Shared,
                Instruments = Instruments.ToDictionary( e => e.Key, e => e.Value ),
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
