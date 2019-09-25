using System.Collections.Generic;

namespace SoundPlayground.Core {
    public enum NoteAccidental {
        Flat = 0, None = 1, Sharp = 2
    }

    public class Note {
        protected static Dictionary<char, int> PitchClassesDictionary = new Dictionary<char, int>() {
            [ 'C' ] = 0,
            [ 'D' ] = 2,
            [ 'E' ] = 4,
            [ 'F' ] = 5,
            [ 'G' ] = 7,
            [ 'A' ] = 9,
            [ 'B' ] = 11
        };

        public static int ParsePitchClass ( string c ) {
            return ParsePitchClass( c.ToCharArray()[ 0 ] );
        }

        public static int ParsePitchClass ( char c ) {
            return PitchClassesDictionary[ char.ToUpper( c ) ];
        }

        public int Start { get; set; } = 0;

        public int PitchClass { get; set; }
        
        public int Duration { get; set; } = 4;

        public int Octave { get; set; } = 4;
        
        public NoteAccidental Accidental { get; set; } = NoteAccidental.None;

        public int ToInteger () {
            int accidental = ( ( int )Accidental - 1 );

            return Octave * 12 + PitchClass + accidental;
        }

        // public static NoteNode FromInteger ( int node ) {

        // }

        public static implicit operator int ( Note note ) => note.ToInteger();

        // public static implicit operator NoteNode ( int note ) => NoteNode.FromInteger( note );
    }
}
