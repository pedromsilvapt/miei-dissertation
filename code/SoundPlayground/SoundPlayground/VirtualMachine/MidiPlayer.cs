using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using NFluidsynth;

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
        
        public int Key { get; set; }

        public int Velocity { get; set; }

        public NoteOnCommand(int timestamp, int key, int velocity)
        {
            Timestamp = timestamp;
            Key = key;
            Velocity = velocity;
        }

        public void Apply(Synth synth)
        {
            Console.WriteLine( $"NoneOn {Timestamp} {Key} {Velocity}" );
            synth.NoteOn(0, Key, Velocity);
        }
    }
    
    public class NoteOffCommand : INoteCommand
    {
        public int Timestamp { get; set; }
        
        public int Key { get; set; }

        public NoteOffCommand(int timestamp, int key)
        {
            Timestamp = timestamp;
            Key = key;
        }

        public void Apply(Synth synth)
        {
            Console.WriteLine( $"NoneOff {Timestamp} {Key}" );
            synth.NoteOff( 0, Key );
        }
    }

    public class MidiPlayer
    {
        public int Tempo { get; set; }

        public List<INoteCommand> Notes { get; set; } = new List<INoteCommand>();

        public string Midi { get; set; } = null;

        public async Task Play()
        {
            using ( var settings = new Settings() ) {
                settings[ConfigurationKeys.AudioDriver].StringValue = "pulseaudio";
                settings[ConfigurationKeys.SynthAudioChannels].IntValue = 2;
                settings[ConfigurationKeys.AudioRealtimePrio].IntValue = 0;
                settings[ConfigurationKeys.SynthVerbose].IntValue = 0;

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
                        
                            foreach (INoteCommand noteCommand in Notes)
                            {
                                if (noteCommand.Timestamp > lastTimestamp)
                                {
                                    await Task.Delay(noteCommand.Timestamp - lastTimestamp);

                                    lastTimestamp = noteCommand.Timestamp;
                                }
                                
                                noteCommand.Apply( syn );
                            }
                        }
                    }
                }
            }
        }
    }
}
