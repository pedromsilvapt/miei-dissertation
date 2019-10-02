using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public abstract class ContextModifierNode : MusicNode {
        public abstract void Modify ( Context context );

        public override IEnumerable<Note> GetCommands ( Context context )
        {
            Modify( context );

            yield break;
        }
    }
}
