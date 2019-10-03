using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class LengthModifierNode : ContextModifierNode {
        public float Length { get; set; }

        public LengthModifierNode ( float length ) {
            Length = length;
        }

        public override void Modify ( Context context ) {
            context.Value = Length;
        }
    }
}
