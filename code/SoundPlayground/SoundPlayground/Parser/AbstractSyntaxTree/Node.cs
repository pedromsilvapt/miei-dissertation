namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class Node
    {
        
    }
    
    public class NoteNode : Node
    {
        public int Note { get; set; }
        
        public int Tempo { get; set; }

        public int Octave { get; set; }
        
        public bool Sharp { get; set; }
    }
}