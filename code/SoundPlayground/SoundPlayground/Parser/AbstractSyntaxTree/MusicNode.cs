using System.Collections.Generic;
using SoundPlayground.Core;
using SoundPlayground.VirtualMachine;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public abstract class MusicNode : Node
    {
        public abstract IEnumerable<Note> GetCommands ( Context context );
    }
}
