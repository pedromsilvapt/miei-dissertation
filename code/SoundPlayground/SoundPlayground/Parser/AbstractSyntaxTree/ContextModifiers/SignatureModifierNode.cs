using System.Collections.Generic;
using SoundPlayground.Core;

namespace SoundPlayground.Parser.AbstractSyntaxTree.ContextModifiers {
    public class SignatureModifierNode : ContextModifierNode {
        public int? Upper { get; set; } = null;

        public int? Lower { get; set; } = null;

        public SignatureModifierNode () {}

        public SignatureModifierNode ( int? upper = null, int? lower = null ) {
            Upper = upper;
            Lower = lower;
        }

        public SignatureModifierNode ( ( int, int ) signature ) : this( signature.Item1, signature.Item2 ) {
            
        }

        public override void Modify ( Context context ) {
            if ( Upper != null && Lower != null ) {
                context.TimeSignature = ( Upper.Value, Lower.Value );
            } else if ( Upper != null ) {
                context.TimeSignature = ( Upper.Value, context.TimeSignature.Item2 );
            } else if ( Lower != null ) {
                context.TimeSignature = ( context.TimeSignature.Item1, Lower.Value );
            }
        }
    }
}
