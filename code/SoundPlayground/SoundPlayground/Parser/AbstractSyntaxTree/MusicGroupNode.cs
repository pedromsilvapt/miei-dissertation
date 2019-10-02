using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class MusicGroupNode : MusicNode
    {
        public MusicNode Expression { get; set; }

        public MusicGroupNode ( MusicNode expression ) {
            Expression = expression;
        }

        public override IEnumerable<Note> GetCommands ( Context context ) {
            Context forked = context.Fork();

            try {
                foreach ( var note in Expression.GetCommands( forked ) ) {
                    yield return note;
                }
            } finally {
                context.Join( forked );
            }
        }
    }
}
