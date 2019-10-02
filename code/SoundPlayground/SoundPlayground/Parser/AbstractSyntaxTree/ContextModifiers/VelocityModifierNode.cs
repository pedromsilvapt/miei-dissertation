using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class VelocityModifierNode : ContextModifierNode {
        public int Velocity { get; set; }

        public VelocityModifierNode ( int velocity ) {
            Velocity = velocity;
        }

        public override void Modify ( Context context ) {
            context.Velocity = Velocity;
        }
    }
}
