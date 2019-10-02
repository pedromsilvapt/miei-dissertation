using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class TempoModifierNode : ContextModifierNode {
        public int Tempo { get; set; }

        public TempoModifierNode ( int tempo ) {
            Tempo = tempo;
        }

        public override void Modify ( Context context ) {
            context.Tempo = Tempo;
        }
    }
}
