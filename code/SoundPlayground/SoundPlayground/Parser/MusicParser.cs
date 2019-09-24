using Superpower;
using System.Collections.Generic;
using System.Linq;
using SoundPlayground.VirtualMachine;

namespace SoundPlayground.Parser {
    public class MusicParser {
        public static List<INoteCommand> Parse (string text) {
            char[] chars = text.ToCharArray();

            List<INoteCommand> commands = new List<INoteCommand>();

            int tempo = 500;
            int velocity = 120;
            int duration = 500;
            int baseKey = 7 * 8;

            int timestamp = 0;

            foreach ( char c in chars ) {
                if ( c != ' ' ) {
                    int key = char.ToLower(c) - 'a';

                    commands.Add( new NoteOnCommand( timestamp, baseKey + key, velocity ) );
                    commands.Add( new NoteOffCommand( timestamp + duration, baseKey + key ) );
                }

                timestamp += tempo;
            }

            return commands.OrderBy( command => command.Timestamp ).ToList();
        }
    }
}
