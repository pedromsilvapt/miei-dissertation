using System.Collections.Generic;
using System.Linq;
using SoundPlayground.Core;
using SoundPlayground.VirtualMachine;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class MusicParallelNode : MusicNode
    {
        public IEnumerable<MusicNode> Expressions { get; set; }

        public MusicParallelNode ( IEnumerable<MusicNode> nodes ) {
            Expressions = nodes;
        }

        public override IEnumerable<Note> GetCommands ( Context context ) {
            List<Context> forks = new List<Context>();

            IEnumerable<Note> notes = Expressions.Select( s => {
                Context forked = context.Fork();

                forks.Add( forked );

                return s.GetCommands( forked );
            } ).MergeSorted( note => note.Start );

            foreach ( Note note in notes ) {
                yield return note;
            }

            context.Join( forks.ToArray() );
        }
    }
}
