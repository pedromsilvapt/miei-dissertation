using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree
{
    public class NoteNode : MusicNode
    {
        public string PitchClass { get; set; }
        
        public int? Value { get; set; }

        public int? Octave { get; set; }
        
        public NoteAccidental Accidental { get; set; } = NoteAccidental.None;

        public override IEnumerable<Note> GetCommands ( Context context ) {
            var note = new Note() { 
                Start = context.Cursor, 
                PitchClass = Note.ParsePitchClass( PitchClass ), 
                Duration = context.GetDuration( Value ?? context.Value ),
                Octave = Octave ?? context.Octave,
                Channel = context.Channel,
                Velocity = context.Velocity, 
                Accidental = Accidental
            };

            context.Cursor += note.Duration;

            yield return note;
        }
    }
}
