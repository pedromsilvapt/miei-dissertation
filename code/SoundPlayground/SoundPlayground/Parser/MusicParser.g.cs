// -----------------------------------------------------------------------
// <auto-generated>
//   This code was generated by Pegasus 4.1.0.0
//
//   Changes to this file may cause incorrect behavior and will be lost if
//   the code is regenerated.
// </auto-generated>
// -----------------------------------------------------------------------

namespace
#line 1 "MusicParser.peg"
           SoundPlayground.Parser
#line default
{
    using System;
    using System.Collections.Generic;
    using Pegasus.Common;
    using
        #line 3 "MusicParser.peg"
       System.Globalization
        #line default
        ;
    using
        #line 4 "MusicParser.peg"
       SoundPlayground.Parser.AbstractSyntaxTree
        #line default
        ;

    /// <summary>
    ///  Parses a string according to the rules of the <see cref="MusicParser" /> grammar.
    /// </summary>
    [System.CodeDom.Compiler.GeneratedCode("Pegasus", "4.1.0.0")]
    public
    partial class
    #line 2 "MusicParser.peg"
           MusicParser
    #line default
    {

        /// <summary>
        ///  Parses a string according to the rules of the <see cref="MusicParser" /> grammar.
        /// </summary>
        /// <param name="subject">The parsing subject.</param>
        /// <param name="fileName">The optional file name to use in error messages.</param>
        /// <returns>The <see cref="MusicNode" /> parsed from <paramref name="subject" />.</returns>
        /// <exception cref="FormatException">
        ///  Thrown when parsing fails against <paramref name="subject"/>.  The exception's <code>Data["cursor"]</code> will be set with the cursor where the fatal error occurred.
        /// </exception>
        public MusicNode Parse(string subject, string fileName = null)
        {
            var cursor = new Cursor(subject, 0, fileName);
            return this.StartRuleHelper(cursor, this.body, "body").Value;
        }

        private IParseResult<
            #line 6 "MusicParser.peg"
      MusicNode
            #line default
            > body(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            var startCursor0 = cursor;
            IParseResult<MusicNode> r1 = null;
            var eStart = cursor;
            r1 = this.expression(ref cursor);
            var eEnd = cursor;
            var e = ValueOrDefault(r1);
            if (r1 != null)
            {
                IParseResult<string> r2 = null;
                r2 = this.EOF(ref cursor);
                if (r2 != null)
                {
                    r0 = this.ReturnHelper<MusicNode>(startCursor0, ref cursor, state =>
                        #line 7 "MusicParser.peg"
                         e
                        #line default
                        );
                }
                else
                {
                    cursor = startCursor0;
                }
            }
            else
            {
                cursor = startCursor0;
            }
            return r0;
        }

        private IParseResult<
            #line 9 "MusicParser.peg"
            MusicNode
            #line default
            > expression(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            r0 = this.parallel(ref cursor);
            return r0;
        }

        private IParseResult<
            #line 12 "MusicParser.peg"
       MusicGroupNode
            #line default
            > group(ref Cursor cursor)
        {
            IParseResult<MusicGroupNode> r0 = null;
            var startCursor0 = cursor;
            IParseResult<string> r1 = null;
            r1 = this.ParseLiteral(ref cursor, "(");
            if (r1 != null)
            {
                IParseResult<IList<string>> r2 = null;
                r2 = this._(ref cursor);
                if (r2 != null)
                {
                    IParseResult<MusicNode> r3 = null;
                    var eStart = cursor;
                    r3 = this.expression(ref cursor);
                    var eEnd = cursor;
                    var e = ValueOrDefault(r3);
                    if (r3 != null)
                    {
                        IParseResult<IList<string>> r4 = null;
                        r4 = this._(ref cursor);
                        if (r4 != null)
                        {
                            IParseResult<string> r5 = null;
                            r5 = this.ParseLiteral(ref cursor, ")");
                            if (r5 != null)
                            {
                                r0 = this.ReturnHelper<MusicGroupNode>(startCursor0, ref cursor, state =>
                                    #line 13 "MusicParser.peg"
                                 new MusicGroupNode( e )
                                    #line default
                                    );
                            }
                            else
                            {
                                cursor = startCursor0;
                            }
                        }
                        else
                        {
                            cursor = startCursor0;
                        }
                    }
                    else
                    {
                        cursor = startCursor0;
                    }
                }
                else
                {
                    cursor = startCursor0;
                }
            }
            else
            {
                cursor = startCursor0;
            }
            return r0;
        }

        private IParseResult<
            #line 15 "MusicParser.peg"
          MusicNode
            #line default
            > parallel(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            var startCursor0 = cursor;
            IParseResult<IList<MusicNode>> r1 = null;
            var nsStart = cursor;
            var startCursor1 = cursor;
            var l0 = new List<MusicNode>();
            while (true)
            {
                var startCursor2 = cursor;
                if (l0.Count > 0)
                {
                    IParseResult<string> r2 = null;
                    var startCursor3 = cursor;
                    IParseResult<IList<string>> r3 = null;
                    r3 = this._(ref cursor);
                    if (r3 != null)
                    {
                        IParseResult<string> r4 = null;
                        r4 = this.ParseLiteral(ref cursor, "|");
                        if (r4 != null)
                        {
                            IParseResult<IList<string>> r5 = null;
                            r5 = this._(ref cursor);
                            if (r5 != null)
                            {
                                {
                                    var len = cursor.Location - startCursor3.Location;
                                    r2 = this.ReturnHelper<string>(startCursor3, ref cursor, state =>
                                        state.Subject.Substring(startCursor3.Location, len)
                                        );
                                }
                            }
                            else
                            {
                                cursor = startCursor3;
                            }
                        }
                        else
                        {
                            cursor = startCursor3;
                        }
                    }
                    else
                    {
                        cursor = startCursor3;
                    }
                    if (r2 == null)
                    {
                        break;
                    }
                }
                IParseResult<MusicNode> r6 = null;
                r6 = this.sequence(ref cursor);
                if (r6 != null)
                {
                    l0.Add(r6.Value);
                }
                else
                {
                    cursor = startCursor2;
                    break;
                }
            }
            if (l0.Count >= 1)
            {
                r1 = this.ReturnHelper<IList<MusicNode>>(startCursor1, ref cursor, state => l0.AsReadOnly());
            }
            else
            {
                cursor = startCursor1;
            }
            var nsEnd = cursor;
            var ns = ValueOrDefault(r1);
            if (r1 != null)
            {
                r0 = this.ReturnHelper<MusicNode>(startCursor0, ref cursor, state =>
                    #line 16 "MusicParser.peg"
                                ns.Count == 1 ? ns[ 0 ] : new MusicParallelNode( ns )
                    #line default
                    );
            }
            else
            {
                cursor = startCursor0;
            }
            return r0;
        }

        private IParseResult<
            #line 18 "MusicParser.peg"
          MusicNode
            #line default
            > sequence(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            var startCursor0 = cursor;
            IParseResult<IList<MusicNode>> r1 = null;
            var nsStart = cursor;
            var startCursor1 = cursor;
            var l0 = new List<MusicNode>();
            while (true)
            {
                var startCursor2 = cursor;
                if (l0.Count > 0)
                {
                    IParseResult<IList<string>> r2 = null;
                    r2 = this._(ref cursor);
                    if (r2 == null)
                    {
                        break;
                    }
                }
                IParseResult<MusicNode> r3 = null;
                r3 = this.repeat(ref cursor);
                if (r3 != null)
                {
                    l0.Add(r3.Value);
                }
                else
                {
                    cursor = startCursor2;
                    break;
                }
            }
            if (l0.Count >= 1)
            {
                r1 = this.ReturnHelper<IList<MusicNode>>(startCursor1, ref cursor, state => l0.AsReadOnly());
            }
            else
            {
                cursor = startCursor1;
            }
            var nsEnd = cursor;
            var ns = ValueOrDefault(r1);
            if (r1 != null)
            {
                r0 = this.ReturnHelper<MusicNode>(startCursor0, ref cursor, state =>
                    #line 19 "MusicParser.peg"
                        ns.Count == 1 ? ns[ 0 ] : new MusicSequenceNode( ns )
                    #line default
                    );
            }
            else
            {
                cursor = startCursor0;
            }
            return r0;
        }

        private IParseResult<
            #line 21 "MusicParser.peg"
        MusicNode
            #line default
            > repeat(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            if (r0 == null)
            {
                var startCursor0 = cursor;
                IParseResult<MusicNode> r1 = null;
                var eStart = cursor;
                r1 = this.expression_unambiguous(ref cursor);
                var eEnd = cursor;
                var e = ValueOrDefault(r1);
                if (r1 != null)
                {
                    IParseResult<IList<string>> r2 = null;
                    r2 = this._(ref cursor);
                    if (r2 != null)
                    {
                        IParseResult<string> r3 = null;
                        r3 = this.ParseLiteral(ref cursor, "*");
                        if (r3 != null)
                        {
                            IParseResult<IList<string>> r4 = null;
                            r4 = this._(ref cursor);
                            if (r4 != null)
                            {
                                IParseResult<int> r5 = null;
                                var cStart = cursor;
                                r5 = this.integer(ref cursor);
                                var cEnd = cursor;
                                var c = ValueOrDefault(r5);
                                if (r5 != null)
                                {
                                    r0 = this.ReturnHelper<MusicNode>(startCursor0, ref cursor, state =>
                                        #line 22 "MusicParser.peg"
                                                   new MusicRepeatNode( e, c )
                                        #line default
                                        );
                                }
                                else
                                {
                                    cursor = startCursor0;
                                }
                            }
                            else
                            {
                                cursor = startCursor0;
                            }
                        }
                        else
                        {
                            cursor = startCursor0;
                        }
                    }
                    else
                    {
                        cursor = startCursor0;
                    }
                }
                else
                {
                    cursor = startCursor0;
                }
            }
            if (r0 == null)
            {
                r0 = this.expression_unambiguous(ref cursor);
            }
            return r0;
        }

        private IParseResult<
            #line 25 "MusicParser.peg"
                        MusicNode
            #line default
            > expression_unambiguous(ref Cursor cursor)
        {
            IParseResult<MusicNode> r0 = null;
            if (r0 == null)
            {
                r0 = this.group(ref cursor);
            }
            if (r0 == null)
            {
                r0 = this.note(ref cursor);
            }
            return r0;
        }

        private IParseResult<
            #line 28 "MusicParser.peg"
      NoteNode
            #line default
            > note(ref Cursor cursor)
        {
            IParseResult<NoteNode> r0 = null;
            if (r0 == null)
            {
                var startCursor0 = cursor;
                IParseResult<string> r1 = null;
                var nStart = cursor;
                r1 = this.ParseClass(ref cursor, "azAZ");
                var nEnd = cursor;
                var n = ValueOrDefault(r1);
                if (r1 != null)
                {
                    IParseResult<IList<string>> r2 = null;
                    r2 = this._(ref cursor);
                    if (r2 != null)
                    {
                        IParseResult<int> r3 = null;
                        var octaveStart = cursor;
                        r3 = this.integer(ref cursor);
                        var octaveEnd = cursor;
                        var octave = ValueOrDefault(r3);
                        if (r3 != null)
                        {
                            IParseResult<IList<string>> r4 = null;
                            r4 = this._(ref cursor);
                            if (r4 != null)
                            {
                                IParseResult<string> r5 = null;
                                r5 = this.ParseLiteral(ref cursor, "/");
                                if (r5 != null)
                                {
                                    IParseResult<IList<string>> r6 = null;
                                    r6 = this._(ref cursor);
                                    if (r6 != null)
                                    {
                                        IParseResult<int> r7 = null;
                                        var durationStart = cursor;
                                        r7 = this.integer(ref cursor);
                                        var durationEnd = cursor;
                                        var duration = ValueOrDefault(r7);
                                        if (r7 != null)
                                        {
                                            r0 = this.ReturnHelper<NoteNode>(startCursor0, ref cursor, state =>
                                                #line 29 "MusicParser.peg"
                                                               new NoteNode() { PitchClass = n, Duration = duration, Octave = octave }
                                                #line default
                                                );
                                        }
                                        else
                                        {
                                            cursor = startCursor0;
                                        }
                                    }
                                    else
                                    {
                                        cursor = startCursor0;
                                    }
                                }
                                else
                                {
                                    cursor = startCursor0;
                                }
                            }
                            else
                            {
                                cursor = startCursor0;
                            }
                        }
                        else
                        {
                            cursor = startCursor0;
                        }
                    }
                    else
                    {
                        cursor = startCursor0;
                    }
                }
                else
                {
                    cursor = startCursor0;
                }
            }
            if (r0 == null)
            {
                var startCursor1 = cursor;
                IParseResult<string> r8 = null;
                var nStart = cursor;
                r8 = this.ParseClass(ref cursor, "azAZ");
                var nEnd = cursor;
                var n = ValueOrDefault(r8);
                if (r8 != null)
                {
                    IParseResult<IList<string>> r9 = null;
                    r9 = this._(ref cursor);
                    if (r9 != null)
                    {
                        IParseResult<string> r10 = null;
                        r10 = this.ParseLiteral(ref cursor, "/");
                        if (r10 != null)
                        {
                            IParseResult<IList<string>> r11 = null;
                            r11 = this._(ref cursor);
                            if (r11 != null)
                            {
                                IParseResult<int> r12 = null;
                                var durationStart = cursor;
                                r12 = this.integer(ref cursor);
                                var durationEnd = cursor;
                                var duration = ValueOrDefault(r12);
                                if (r12 != null)
                                {
                                    r0 = this.ReturnHelper<NoteNode>(startCursor1, ref cursor, state =>
                                        #line 30 "MusicParser.peg"
                                                               new NoteNode() { PitchClass = n, Duration = duration }
                                        #line default
                                        );
                                }
                                else
                                {
                                    cursor = startCursor1;
                                }
                            }
                            else
                            {
                                cursor = startCursor1;
                            }
                        }
                        else
                        {
                            cursor = startCursor1;
                        }
                    }
                    else
                    {
                        cursor = startCursor1;
                    }
                }
                else
                {
                    cursor = startCursor1;
                }
            }
            if (r0 == null)
            {
                var startCursor2 = cursor;
                IParseResult<string> r13 = null;
                var nStart = cursor;
                r13 = this.ParseClass(ref cursor, "azAZ");
                var nEnd = cursor;
                var n = ValueOrDefault(r13);
                if (r13 != null)
                {
                    IParseResult<IList<string>> r14 = null;
                    r14 = this._(ref cursor);
                    if (r14 != null)
                    {
                        IParseResult<int> r15 = null;
                        var octaveStart = cursor;
                        r15 = this.integer(ref cursor);
                        var octaveEnd = cursor;
                        var octave = ValueOrDefault(r15);
                        if (r15 != null)
                        {
                            r0 = this.ReturnHelper<NoteNode>(startCursor2, ref cursor, state =>
                                #line 31 "MusicParser.peg"
                                                               new NoteNode() { PitchClass = n, Octave = octave }
                                #line default
                                );
                        }
                        else
                        {
                            cursor = startCursor2;
                        }
                    }
                    else
                    {
                        cursor = startCursor2;
                    }
                }
                else
                {
                    cursor = startCursor2;
                }
            }
            if (r0 == null)
            {
                var startCursor3 = cursor;
                IParseResult<string> r16 = null;
                var nStart = cursor;
                r16 = this.ParseClass(ref cursor, "azAZ");
                var nEnd = cursor;
                var n = ValueOrDefault(r16);
                if (r16 != null)
                {
                    r0 = this.ReturnHelper<NoteNode>(startCursor3, ref cursor, state =>
                        #line 32 "MusicParser.peg"
                                                               new NoteNode() { PitchClass = n }
                        #line default
                        );
                }
                else
                {
                    cursor = startCursor3;
                }
            }
            return r0;
        }

        private IParseResult<
            #line 34 "MusicParser.peg"
         int
            #line default
            > integer(ref Cursor cursor)
        {
            IParseResult<int> r0 = null;
            var startCursor0 = cursor;
            IParseResult<IList<string>> r1 = null;
            var dStart = cursor;
            var startCursor1 = cursor;
            var l0 = new List<string>();
            while (true)
            {
                IParseResult<string> r2 = null;
                r2 = this.ParseClass(ref cursor, "09");
                if (r2 != null)
                {
                    l0.Add(r2.Value);
                }
                else
                {
                    break;
                }
            }
            if (l0.Count >= 1)
            {
                r1 = this.ReturnHelper<IList<string>>(startCursor1, ref cursor, state => l0.AsReadOnly());
            }
            else
            {
                cursor = startCursor1;
            }
            var dEnd = cursor;
            var d = ValueOrDefault(r1);
            if (r1 != null)
            {
                r0 = this.ReturnHelper<int>(startCursor0, ref cursor, state =>
                    #line 35 "MusicParser.peg"
                   int.Parse( string.Join( "", d ) )
                    #line default
                    );
            }
            else
            {
                cursor = startCursor0;
            }
            return r0;
        }

        private IParseResult<IList<string>> _(ref Cursor cursor)
        {
            IParseResult<IList<string>> r0 = null;
            var startCursor0 = cursor;
            var l0 = new List<string>();
            while (true)
            {
                IParseResult<string> r1 = null;
                r1 = this.ParseClass(ref cursor, "  \t\t");
                if (r1 != null)
                {
                    l0.Add(r1.Value);
                }
                else
                {
                    break;
                }
            }
            r0 = this.ReturnHelper<IList<string>>(startCursor0, ref cursor, state => l0.AsReadOnly());
            return r0;
        }

        private IParseResult<string> EOF(ref Cursor cursor)
        {
            IParseResult<string> r0 = null;
            if (r0 == null)
            {
                var startCursor0 = cursor;
                IParseResult<string> r1 = null;
                r1 = this.ParseAny(ref cursor);
                if (r1 == null)
                {
                    r0 = this.ReturnHelper<string>(cursor, ref cursor, state => string.Empty);
                }
                else
                {
                    cursor = startCursor0;
                }
            }
            if (r0 == null)
            {
                var startCursor1 = cursor;
                IParseResult<string> r2 = null;
                var unexpectedStart = cursor;
                r2 = this.ParseAny(ref cursor);
                var unexpectedEnd = cursor;
                var unexpected = ValueOrDefault(r2);
                if (r2 != null)
                {
                    throw this.ExceptionHelper(cursor, state =>
                        #line 41 "MusicParser.peg"
                         "Unexpected character '" + unexpected + "'."
                        #line default
                        );
                }
                else
                {
                    cursor = startCursor1;
                }
            }
            return r0;
        }

        private IParseResult<T> StartRuleHelper<T>(Cursor cursor, ParseDelegate<T> startRule, string ruleName)
        {
            var result = startRule(ref cursor);
            if (result == null)
            {
                throw ExceptionHelper(cursor, state => "Failed to parse '" + ruleName + "'.");
            }
            return result;
        }

        private IParseResult<string> ParseLiteral(ref Cursor cursor, string literal, bool ignoreCase = false)
        {
            if (cursor.Location + literal.Length <= cursor.Subject.Length)
            {
                var substr = cursor.Subject.Substring(cursor.Location, literal.Length);
                if (ignoreCase ? substr.Equals(literal, StringComparison.OrdinalIgnoreCase) : substr == literal)
                {
                    var endCursor = cursor.Advance(substr.Length);
                    var result = this.ReturnHelper<string>(cursor, ref endCursor, state => substr);
                    cursor = endCursor;
                    return result;
                }
            }
            return null;
        }

        private IParseResult<string> ParseClass(ref Cursor cursor, string characterRanges, bool negated = false, bool ignoreCase = false)
        {
            if (cursor.Location + 1 <= cursor.Subject.Length)
            {
                var c = cursor.Subject[cursor.Location];
                bool match = false;
                for (int i = 0; !match && i < characterRanges.Length; i += 2)
                {
                    match = c >= characterRanges[i] && c <= characterRanges[i + 1];
                }
                if (!match && ignoreCase && (char.IsUpper(c) || char.IsLower(c)))
                {
                    var cs = c.ToString();
                    for (int i = 0; !match && i < characterRanges.Length; i += 2)
                    {
                        var min = characterRanges[i];
                        var max = characterRanges[i + 1];
                        for (char o = min; !match && o <= max; o++)
                        {
                            match = (char.IsUpper(o) || char.IsLower(o)) && cs.Equals(o.ToString(), StringComparison.CurrentCultureIgnoreCase);
                        }
                    }
                }
                if (match ^ negated)
                {
                    var endCursor = cursor.Advance(1);
                    var substr = cursor.Subject.Substring(cursor.Location, 1);
                    var result = this.ReturnHelper<string>(cursor, ref endCursor, state => substr);
                    cursor = endCursor;
                    return result;
                }
            }
            return null;
        }

        private IParseResult<string> ParseAny(ref Cursor cursor)
        {
            if (cursor.Location + 1 <= cursor.Subject.Length)
            {
                var substr = cursor.Subject.Substring(cursor.Location, 1);
                var endCursor = cursor.Advance(1);
                var result = this.ReturnHelper<string>(cursor, ref endCursor, state => substr);
                cursor = endCursor;
                return result;
            }
            return null;
        }

        private IParseResult<T> ReturnHelper<T>(Cursor startCursor, ref Cursor endCursor, Func<Cursor, T> wrappedCode)
        {
            var result = wrappedCode(endCursor);
            var lexical = result as ILexical;
            if (lexical != null && lexical.StartCursor == null && lexical.EndCursor == null)
            {
                lexical.StartCursor = startCursor;
                lexical.EndCursor = endCursor;
            }
            return new ParseResult<T>(startCursor, endCursor, result);
        }

        private IParseResult<T> ParseHelper<T>(ref Cursor cursor, ParseDelegate<T> wrappedCode)
        {
            var startCursor = cursor;
            var result = wrappedCode(ref cursor);
            if (result == null)
            {
                cursor = startCursor;
                return null;
            }
            else
            {
                cursor = cursor.WithMutability(false);
                return result;
            }
        }

        private Exception ExceptionHelper(Cursor cursor, Func<Cursor, string> wrappedCode)
        {
            var ex = new FormatException(wrappedCode(cursor));
            ex.Data["cursor"] = cursor;
            return ex;
        }

        private T ValueOrDefault<T>(IParseResult<T> result)
        {
            return result == null
                ? default(T)
                : result.Value;
        }
    }
}
