using System;
using System.Collections.Generic;
using System.Linq;

namespace SoundPlayground.Core {
    public class SharedContext {
        public int ChannelCount { get; set; } = 24;

        public Dictionary<int, Instrument> Channels { get; set; } = new Dictionary<int, Instrument>();

        public IEnumerable<int> AvailableChannels {
            get {
                return Enumerable.Range( 0, ChannelCount ).Where( c => !Channels.ContainsKey( c ) );
            }
        }

        public void RegisterInstrument ( Instrument instrument ) {
            int? channel = AvailableChannels.Select( a => (int?)a ).FirstOrDefault();

            if ( channel == null ) {
                throw new System.Exception( "No channel available found." );
            }

            Channels[ channel.Value ] = instrument;

            instrument.Channel = channel.Value;
        }

        public void UnregisterInstrument ( Instrument instrument ) {
            Channels.Remove( instrument.Channel.Value );

            instrument.Channel = null;
        }
    }
}
