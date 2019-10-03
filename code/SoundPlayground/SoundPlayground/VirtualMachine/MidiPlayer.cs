using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
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

        public bool ReverbEnabled { get; set; } = true;

        public double ReverbRoomSize { get; set; } = 0.8f;
        
        public double ReverbDamping { get; set; } = 0.6f;

        public double ReverbWidth { get; set; } = 0.5f;

        public double ReverbLevel { get; set; } = 0.5f;

        public bool ChorusEnabled { get; set; } = false;

        public int ChorusNumVoices { get; set; }

        public double ChorusLevel { get; set; }
        
        public double ChorusSpeed { get; set; }

        public double ChorusDepthMS { get; set; }

        public FluidChorusMod ChorusMod { get; set; } = FluidChorusMod.Sine;

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
                settings[ConfigurationKeys.AudioPeriodSize].IntValue = 1024;
                settings[ConfigurationKeys.SynthReverbActive].IntValue = ReverbEnabled ? 1 : 0;
                settings[ConfigurationKeys.SynthChorusActive].IntValue = ChorusEnabled ? 1 : 0;

                using ( var syn = new Synth(settings) ) {
                    syn.LoadSoundFont("/usr/share/sounds/sf2/FluidR3_GM.sf2", true);

                    using ( var adriver = new AudioDriver(syn.Settings, syn) ) {
                        syn.SetReverb( ReverbRoomSize, ReverbDamping, ReverbWidth, ReverbLevel );
                        syn.SetChorus( ChorusNumVoices, ChorusLevel, ChorusSpeed, ChorusDepthMS, ChorusMod );

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
                            var sw = new System.Diagnostics.Stopwatch();
                            sw.Start();

                            // Explaining the timer process used
                            // All note commands (NoteOn/NoteOff) are ordered by their noteCommand.Timestamp (value in milliseconds relative to the beginning
                            // of the music). Let's imagine that two of them are, for example, one second apart. Ideally, we would want to do a
                            // Thread.Sleep( 1000 ) and hope that the thread would unblock exactly 1000 milliseconds after. However, the system's clock
                            // resolution varies between different Operating Systems and different physical Processors. So we could not be sure when the thread
                            // would be woken. Instead we do a Thread.Sleep( 1000 - minResolution ), which hopefully means that our thread will awake before the note is due
                            // Three things can happen now:
                            //   - We can be early, i.e. we still have to wait a bit, and for that we use a simple loop with a high-precision Stopwatch
                            //   - We can be on time, in which case we just play the note
                            //   - We can be late, in wich case we play the note right away and add to the drift variable how late we are
                            // Every subsequent timestamp will have the drift variable added to it to compensate

                            int minResolution = 30;
                            int drift = 0;

                            foreach ( INoteCommand noteCommand in BuildCommands( Notes ) )
                            {
                                int timestamp = noteCommand.Timestamp + drift;

                                int elapsed = (int)sw.Elapsed.TotalMilliseconds;

                                if ( timestamp - minResolution > elapsed )
                                {
                                    await Task.Delay( Math.Max( 0, timestamp - elapsed - minResolution ) );
                                }

                                while ( timestamp > sw.Elapsed.TotalMilliseconds ) { 
                                    Thread.Sleep( 0 );
                                }

                                elapsed = (int)sw.Elapsed.TotalMilliseconds;

                                noteCommand.Apply( syn );

                                if ( timestamp < elapsed ) drift += elapsed - timestamp;
                            }

                            sw.Stop();

                            Console.WriteLine( $"Total drift: {drift}ms out of {sw.Elapsed.TotalMilliseconds}ms" );
                        }
                    }
                }
            }
        }
    }
}
