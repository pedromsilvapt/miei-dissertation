using System;
using System.Numerics;
using ImGuiNET;
using System.Threading.Tasks;
using SoundPlayground.Graphics;
using SoundPlayground.VirtualMachine;
using SoundPlayground.Parser;
using System.Linq;

namespace SoundPlayground
{
    public class Application : BaseApplication
    {
        public string code = "(A3/8*11 G3 F3/8*12) (A3/8*11 | A4/3 C5/3 D5/3 E5)";

        public string codeSample = 
@"# This expression plays the sound
ababcd

# This does not play the notes, and instead saves them in the variable
$notes = ababcd

# Moves the notes 2 octaves up
$notes = uctUp( $notes, 2 )

# Finally plays the notes inside the variable
play( $notes )

fn chords ( $root ) {
    # Will play three notes in parallel expression as ( ( a + $root ) | ( b + $root ) | ( c + $root ) )
    add( ( a | b | c ), $root )
}

# Plays the sound
chords( a )

# Or again can save it to a variable
$notes = chords( a )

# We can define instruments prefixing them with a :
:piano = 'path_to_a_soundfont'
:violin = 'path_to_a_different_soundfont'

# We can use an instrument in any expression, all the notes after the instrument will be played using it
# The pipe character | will play the notes in parallel
( :piano abc | :violin abc )

# We can also set an instrument for an entire block
with :piano { 
    abc

    abab
}
";


        // public string midiFile = @"/home/pedromsilva/Documents/projects/SoundPlayground/Westworld (Piano Cover) - MIDI.mid";

        public string midiFile = @"/home/pedromsilva/Documents/projects/SoundPlayground/Ramin_Djawadi_-_Westworld_Theme.mid";

        public MidiPlayer player = new MidiPlayer();

        public override void Render()
        {
            ImGui.BeginTabBar("main_tag");

            if ( ImGui.BeginTabItem("Editor") ) {
                Vector2 textSize = ImGui.GetContentRegionAvail() - new Vector2( 0, 30 );

                ImGui.InputTextMultiline("Code", ref code, 1000, textSize);

                if (ImGui.Button("Play"))
                {
                    var player = new MidiPlayer() { Notes = new MusicParser().Parse( code ).GetCommands( new Context() { BPM = 105 } ).ToList() };
                    // var player = new MidiPlayer() { Notes = null };
                    
                    Async( () => Task.Factory.StartNew( () => player.Play(), TaskCreationOptions.LongRunning ) );
                }
                
                ImGui.EndTabItem();
            }

            if ( ImGui.BeginTabItem( "Sample" ) ) {
                ImGui.InputTextMultiline( "Code Sample", ref codeSample, 1000, new Vector2( -1, -1 ) );

                ImGui.EndTabItem();
            }

            if ( ImGui.BeginTabItem("Midi") ) {
                ImGui.InputText("MIDI File", ref midiFile, 1000);

                if ( ImGui.Button("Play") ) {
                    var player = new MidiPlayer() { Midi = midiFile };

                    Async( () => Task.Factory.StartNew( () => player.Play(), TaskCreationOptions.LongRunning ) );
                }

                ImGui.EndTabItem();
            }
        }
    }
}
