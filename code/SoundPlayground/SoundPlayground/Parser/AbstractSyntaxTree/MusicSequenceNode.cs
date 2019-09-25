using System.Collections.Generic;
using SoundPlayground.Core;
using SoundPlayground.VirtualMachine;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class MusicSequenceNode : MusicNode
    {
        public IEnumerable<MusicNode> Expressions { get; set; }

        public MusicSequenceNode ( IEnumerable<MusicNode> nodes ) {
            Expressions = nodes;
        }

        public override IEnumerable<Note> GetCommands ( Context context ) {
            foreach ( MusicNode node in Expressions ) {
                foreach ( Note note in node.GetCommands( context ) ) {
                    yield return note;
                }
            }
        }
    }
}
