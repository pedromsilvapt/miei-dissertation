using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public abstract class BlockContextModifierNode : MusicNode {
        public MusicNode Body { get; set; }

        public abstract void Modify ( Context context );

        public abstract void Restore ( Context context );

        public BlockContextModifierNode ( MusicNode body ) {
            Body = body;
        }

        public override IEnumerable<Note> GetCommands ( Context context )
        {
            Context blockContext = context.Fork();

            Modify( blockContext );

            try {
                if ( Body != null ) {
                    foreach ( var command in Body.GetCommands( blockContext ) ) {
                        yield return command;
                    }
                }
            } finally {
                Restore( blockContext );

                context.Join( blockContext );
            }
        }
    }
}
