using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class RestNode : MusicNode
    {
        public float? Value { get; set; }

        public bool Visible { get; set; }

        public override IEnumerable<Note> GetCommands ( Context context ) {
            context.Cursor += context.GetDuration( Value ?? context.Value );

            yield break;
        }
    }
}
