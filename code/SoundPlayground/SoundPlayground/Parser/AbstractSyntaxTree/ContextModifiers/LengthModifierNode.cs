using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class LengthModifierNode : ContextModifierNode {
        public int Length { get; set; }

        public LengthModifierNode ( int length ) {
            Length = length;
        }

        public override void Modify ( Context context ) {
            context.Value = Length;
        }
    }
}
