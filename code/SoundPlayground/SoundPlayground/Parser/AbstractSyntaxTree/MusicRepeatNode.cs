using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class MusicRepeatNode : MusicNode
    {
        public MusicNode Expression { get; set; }

        public int Count { get; set; }

        public MusicRepeatNode ( MusicNode expression, int count ) {
            Expression = expression;
            Count = count;
        }

        public override IEnumerable<Note> GetCommands ( Context context ) {
            for ( int i = 0; i < Count; i++ ) {
                var ctx = context.Fork();

                try {
                    foreach ( Note note in Expression.GetCommands( ctx ) ) {
                        yield return note;
                    }
                } finally {
                    context.Join( ctx );
                }
            }
        }
    }
}
