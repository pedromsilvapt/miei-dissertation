namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class InstrumentBlockModifier : BlockContextModifierNode
    {
        public string InstrumentName { get; set; }

        public InstrumentBlockModifier ( MusicNode body, string instrumentName ) : base( body ) {
            InstrumentName = instrumentName;
        }

        public override void Modify ( Context context )
        {
            if ( !context.Instruments.ContainsKey( InstrumentName ) ) {
                throw new System.Exception( $"Could not switch to non-existent instrument {InstrumentName}" );
            }

            var instrument = context.Instruments[ InstrumentName ];

            if ( instrument.Channel == null ) {
                context.Shared.RegisterInstrument( instrument );
            }

            instrument.RefCount++;

            context.Channel = instrument.Channel.Value;
        }

        public override void Restore ( Context context )
        {
            var instrument = context.Instruments[ InstrumentName ];

            instrument.RefCount--;

            if ( instrument.RefCount == 0 ) {
                context.Shared.UnregisterInstrument( instrument );
            }
        }
    }
}
