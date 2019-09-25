using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class NoteNode : MusicNode
    {
        public string PitchClass { get; set; }
        
        public int? Duration { get; set; }

        public int? Octave { get; set; }
        
        public NoteAccidental Accidental { get; set; } = NoteAccidental.None;

        public override IEnumerable<Note> GetCommands ( Context context ) {
            var note = new Note() { 
                Start = context.Cursor, 
                PitchClass = Note.ParsePitchClass( PitchClass ), 
                Duration = context.CalculateDurationInMilliseconds( Duration ?? context.Duration ),
                Octave = Octave ?? context.Octave, 
                Accidental = Accidental 
            };

            yield return note;

            context.Cursor += note.Duration;
        }
    }
}
