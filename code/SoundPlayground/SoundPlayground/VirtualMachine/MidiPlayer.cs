using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using NFluidsynth;
using SoundPlayground.Core;
using SoundPlayground.Parser.AbstractSyntaxTree;

namespace SoundPlayground.VirtualMachine
{
    public interface INoteCommand
    {
        int Timestamp { get; set; }

        void Apply(Synth synth);
    }

    public class NoteOnCommand : INoteCommand
    {
        public int Timestamp { get; set; }
        
        public int Channel { get; set; } = 0;

        public int Key { get; set; }

        public int Velocity { get; set; } = 127;

        public NoteOnCommand(int timestamp, int channel, int key, int velocity)
        {
            Timestamp = timestamp;
            Channel = channel;
            Key = key;
            Velocity = velocity;
        }

        public void Apply(Synth synth)
        {
            synth.NoteOn( Channel, Key, Velocity );
        }

        public override string ToString() {
            return $"<NoteOn Timestamp={Timestamp} Channel={Channel} Key={Key} Velocity={Velocity}>";
        }
    }
    
    public class NoteOffCommand : INoteCommand
    {
        public int Timestamp { get; set; }
        
        public int Channel { get; set; } = 0;

        public int Key { get; set; }

        public NoteOffCommand(int timestamp, int channel, int key)
        {
            Timestamp = timestamp;
            Channel = channel;
            Key = key;
        }

        public void Apply(Synth synth)
        {
            synth.NoteOff( Channel, Key );
        }

        public override string ToString() {
            return $"<NoneOff Timestamp={Timestamp} Channel={Channel} Key={Key}>";
        }
    }

    public class MidiPlayer
    {
        public int Tempo { get; set; }

        public IList<Note> Notes { get; set; } = new List<Note>();

        public string Midi { get; set; } = null;

        public IEnumerable<INoteCommand> BuildCommands ( IEnumerable<Note> notes ) {
            List<INoteCommand> commands = new List<INoteCommand>();

            foreach ( Note note in notes ) {
                int key = note.ToInteger();

                commands.Add( new NoteOnCommand( note.Start, note.Channel, key, note.Velocity ) );
                commands.Add( new NoteOffCommand( note.Start + note.Duration, note.Channel, key ) );
            }

            return commands.OrderBy( command => command.Timestamp ).ToList();
        }

        public async Task Play()
        {
            using ( var settings = new Settings() ) {
                settings[ConfigurationKeys.AudioDriver].StringValue = "pulseaudio";
                settings[ConfigurationKeys.SynthAudioChannels].IntValue = 2;
                settings[ConfigurationKeys.AudioRealtimePrio].IntValue = 0;
                settings[ConfigurationKeys.SynthVerbose].IntValue = 0;
                settings[ConfigurationKeys.AudioPeriods].IntValue = 2;
                settings[ConfigurationKeys.AudioPeriodSize].IntValue = 4096;

                using ( var syn = new Synth(settings) ) {
                    syn.LoadSoundFont("/usr/share/sounds/sf2/FluidR3_GM.sf2", true);

                    using ( var adriver = new AudioDriver(syn.Settings, syn) ) {
                        if ( Midi != null ) {
                            // Meanwhile we are cheating a little bit and using the build-in FluidSynth MIDI player
                            // In the future it would be nice to read the events from the MIDI file and play them ourselves
                            // That way we could mix MIDI files with our own music expressions, and maybe even transform MIDI files
                            using ( var player = new Player( syn ) ) {
                                player.Add( Midi );
                                player.Play();
                                // Synchronous join. Thankfully this code runs in a separate thread. Would be nice to have a async version
                                player.Join();
                            }
                        } else {
                            int lastTimestamp = 0;
                        
                            // syn.ProgramChange( 0, 5 );

                            Console.WriteLine( $"{ Notes.Count } notes" );

                            long drift = 0;

                            foreach ( INoteCommand noteCommand in BuildCommands( Notes ) )
                            {
                                if ( noteCommand.Timestamp > lastTimestamp )
                                {
                                    var time = DateTimeOffset.Now.ToUnixTimeMilliseconds();

                                    await Task.Delay( noteCommand.Timestamp - lastTimestamp );
                                    //new System.Threading.ManualResetEvent(false).WaitOne( noteCommand.Timestamp - lastTimestamp );

                                    drift += Math.Abs( ( DateTimeOffset.Now.ToUnixTimeMilliseconds() - time ) - ( noteCommand.Timestamp - lastTimestamp ) );

                                    lastTimestamp = noteCommand.Timestamp;
                                }
                                
                                noteCommand.Apply( syn );
                            }

                            Console.WriteLine( $"Total drift: {drift}ms out of {lastTimestamp}ms" );
                        }
                    }
                }
            }
        }
    }
}
