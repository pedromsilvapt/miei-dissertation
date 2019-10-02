using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class OctaveModifierNode : ContextModifierNode {
        public int Octave { get; set; }

        public OctaveModifierNode ( int octave ) {
            Octave = octave;
        }

        public override void Modify ( Context context ) {
            context.Octave = Octave;
        }
    }
}
