using System;
using System.Numerics;
using ImGuiNET;
using System.Threading.Tasks;
using SoundPlayground.Graphics;
using SoundPlayground.VirtualMachine;
using SoundPlayground.Parser;
using System.Linq;
using System.IO;
using System.Reflection;
using System.Runtime.Loader;
using System.CodeDom.Compiler;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Pegasus;
using Pegasus.Common;
using System.Collections;
using System.Collections.Generic;
using System.Collections.Immutable;
using SoundPlayground.Parser.AbstractSyntaxTree;
using SoundPlayground.Core;

namespace SoundPlayground
{
    public class KeyboardShortcut {
        public string Hotkey = "";

        public string Expression = "";

        public MusicNode Node = null;

        public string ParseError = null;
    }

    public class Application : BaseApplication
    {
        public Vector4 colorRed = new Vector4( 1, 0, 0, 1 );

        public string code =
@"S6/8 T105 L/8 V70
(O3 A*11 G F*12) 
(O3 A*11 | L/3 A4 C5 D5 E5)";
        // public string code = "(A3/2*11 G F3/2*12) (A3/8*11 | A4/3 C5/3 D5/3 E5)";

        public string[] codeCommands = null;

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

        public List<KeyboardShortcut> keyboardKeys = new List<KeyboardShortcut>() {
            new KeyboardShortcut() { Hotkey = "a", Expression = "A3/8*11 | A4/3 C5/3 D5/3 E5" },
            new KeyboardShortcut() { Hotkey = "b", Expression = "A3/8*11 | E5/3 D5/3 C5/3 A4" },
            new KeyboardShortcut() { Hotkey = "c", Expression = "A3/8*11 G3/8 F3/8*12" }
        };

        public MusicParser parser = new MusicParser();

        public MusicNode Parse ( string expression ) {
            // return null;
            return parser.Parse( code );
        }

        public Context CreateContext () {
            return new Context {
                TimeSignature = (6, 8),
                Tempo = 108,
                Velocity = 80
            };
        }

        public override void Render()
        {
            ImGui.BeginTabBar("main_tag");

            if ( ImGui.BeginTabItem("Editor") ) {
                Vector2 textSize = ImGui.GetContentRegionAvail() / new Vector2( 1, 2 );

                ImGui.InputTextMultiline("Code", ref code, 1000, textSize);

                if (ImGui.Button("Play"))
                {
                    var player = new MidiPlayer() { Notes = Parse( code ).GetCommands( CreateContext() ).ToList() };
                    // var player = new MidiPlayer() { Notes = null };
                    
                    Async( () => Task.Factory.StartNew( () => player.Play(), TaskCreationOptions.LongRunning ) );
                }

                ImGui.SameLine();

                if ( ImGui.Button( "See Commands" ) ) {
                    var player = new MidiPlayer() { Notes = Parse( code ).GetCommands( CreateContext() ).ToList() };

                    codeCommands = player.BuildCommands( player.Notes ).Select( command => command.ToString() ).ToArray();
                }
                
                ImGui.SameLine();

                if ( ImGui.Button( "See Notes" ) ) {
                    codeCommands = Parse( code )
                        .GetCommands( CreateContext() )
                        .Select( command => command.ToString() )
                        .ToArray();
                }
                
                ImGui.BeginChildFrame( ImGui.GetID( "commands_list" ), new Vector2( -1, -1 ) );
                
                if ( codeCommands != null ) {
                    foreach ( string cmd in codeCommands ) {
                        ImGui.TextWrapped( cmd );
                    }
                }

                ImGui.EndChildFrame();

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

            if ( ImGui.BeginTabItem( "Keyboard" ) ) {
                int removeIndex = -1;

                for ( int i = 0; i < keyboardKeys.Count; i++ ) {
                    var key = keyboardKeys[ i ];
                    
                    ImGui.PushID( "hotkey-" + i );

                    float maxWidth = ImGui.GetContentRegionAvail().X - ImGui.GetStyle().ItemSpacing.X * 2 - 80;

                    ImGui.SetNextItemWidth( ImGuiUtils.CalcInputWidth( "Hotkey", maxWidth * 0.3f ) );

                    ImGui.InputText( "Hotkey", ref key.Hotkey, 30 );
                    
                    ImGui.SameLine();

                    ImGui.SetNextItemWidth( ImGuiUtils.CalcInputWidth( "Expression", maxWidth * 0.7f ) );

                    if ( ImGui.InputText( "Expression", ref key.Expression, 200 ) ) {
                        key.Node = null;
                    }

                    if ( key.Node == null ) {
                        ImGui.SameLine();

                        if ( ImGui.Button( "Compile" ) ) {
                            try {
                                key.Node = Parse( key.Expression );
                            } catch ( Exception ex ) {
                                key.ParseError = ex.Message;
                            }
                        }

                        ImGui.SameLine();

                        if ( ImGui.Button( "X" ) ) {
                            removeIndex = i;
                        }
                    }

                    if ( key.ParseError != null ) {
                        ImGui.TextColored( colorRed, "!" );

                        if ( ImGui.IsItemHovered() ) {
                            ImGui.SetNextWindowSize(new Vector2( 600, 0 ));

                            ImGui.BeginTooltip();

                            ImGui.TextWrapped( key.ParseError );

                            ImGui.EndTooltip();
                        }
                    }

                    if ( key.Node != null && ImGuiUtils.Hotkey( key.Hotkey[ 0 ] ) ) {
                        var player = new MidiPlayer() { Notes = key.Node.GetCommands( CreateContext() ).ToList() };
                    
                        Async( () => Task.Factory.StartNew( () => player.Play(), TaskCreationOptions.LongRunning ) );
                    }

                    ImGui.PopID();
                }

                if ( removeIndex >= 0 ) {
                    keyboardKeys.RemoveAt( removeIndex );
                }

                if ( ImGui.Button( "Add Key Shortcut", new Vector2( -1, 0 ) ) ) {
                    keyboardKeys.Add( new KeyboardShortcut() );
                }
            }

            ImGui.EndTabBar();

            RenderGrammarInspector();
        }

        // Grammar Inspector
        public float panelInputSize = 20;
        public float panelInspectorSize = 80;

        public float panelContainerSize = 100;

        public string grammarSource = "";

        public string grammarTest = "";

        public dynamic grammarParser = null;

        public int assemblyCount = 0;

        public Dictionary<string, object> grammarInspectorProperties = null;

        private List<string> grammarErrors = new List<string>();

        private List<string> grammarWarnings = new List<string>();

        private string grammarTestError = null;

        public void RenderGrammarInspector () {
            if ( ImGui.Begin( "Grammar" ) ) {
                ImGui.TextDisabled( "README (?)" );

                if ( ImGui.IsItemHovered() ) {
                    ImGui.BeginTooltip();
                    ImGui.Text( "ATTN: Any changes made here will not be saved." );
                    ImGui.Text( "First click on the Compile button, and then the parse button." );
                    ImGui.Text( "Any changes to the grammar require clicking on the Compile button again." );
                    ImGui.EndTooltip();
                }

                ImGui.Columns( 2 );

                ImGui.InputTextMultiline( "###Grammar", ref grammarSource, 5000, new Vector2( -1, ImGui.GetContentRegionAvail().Y - 30 ) );

                if ( ImGui.Button( "1. Compile" ) ) {
                    CompileGrammar();
                }

                if ( grammarWarnings.Count > 0 ) {
                    ImGui.SameLine();

                    ImGui.Text( $"Warnings ({ grammarWarnings.Count })" );

                    if ( ImGui.IsItemHovered() ) {
                        ImGui.SetNextWindowSize(new Vector2( 600, 0 ));
                        ImGui.BeginTooltip();

                        // Debug output. In case your environment is different it may show some messages.
                        foreach ( var compilerMessage in grammarWarnings ) {
                            ImGui.TextWrapped( compilerMessage.ToString() );
                        }
                        
                        ImGui.EndTooltip();
                    }
                }

                if ( grammarErrors.Count > 0 ) {
                    ImGui.SameLine();

                    ImGui.TextColored( colorRed, $"Errors ({ grammarErrors.Count })" );

                    if ( ImGui.IsItemHovered() ) {
                        ImGui.SetNextWindowSize(new Vector2( 600, 0 ));
                        ImGui.BeginTooltip();

                        // Debug output. In case your environment is different it may show some messages.
                        foreach ( var compilerMessage in grammarErrors ) {
                            ImGui.TextWrapped( compilerMessage.ToString() );
                        }
                        
                        ImGui.EndTooltip();
                    }
                }
                
                ImGui.SameLine();

                var saveButtonWidth = ImGuiUtils.CalcButtonSize( "Save to File" );

                var cursor = ImGui.GetCursorPos();
                
                ImGui.SetCursorPosX( cursor.X + ImGui.GetContentRegionAvail().X - saveButtonWidth.X );

                if ( ImGui.Button( "Save to File" ) ) {
                    Async( () => SaveGrammar( grammarSource ) );
                }

                ImGui.SetCursorPos( cursor );

                ImGui.NextColumn();

                DrawSplitter( 20, ref panelContainerSize, ref panelInputSize, ref panelInspectorSize, 50, 50 );

                ImGui.InputTextMultiline( "###Input", ref grammarTest, 5000, new Vector2( -1, panelInputSize - 30 ) );

                if ( ImGui.Button( "2. Parse" ) ) {
                    ParseGrammarInput();
                }

                if ( grammarTestError != null ) {
                    ImGui.SameLine();

                    ImGui.PushStyleColor( ImGuiCol.Text, colorRed );
                    ImGui.TextWrapped( "ERROR: " + grammarTestError );
                    ImGui.PopStyleColor();
                }

                ImGui.BeginChildFrame( ImGui.GetID( "inspector" ), new Vector2( -1, panelInspectorSize ) );

                if ( grammarInspectorProperties == null ) {
                    ImGui.TextDisabled( "Sem resultados a apresentar." );
                } else {
                    RenderInspector( grammarInspectorProperties );
                }

                ImGui.EndChildFrame();

                ImGui.Columns( 1 );

                ImGui.End();
            }
        }

        public void RenderInspector ( Dictionary<string, object> properties, string prefix = null ) {
            string nodeName = $"{properties[ "__type" ]}###{properties[ "__hashCode" ]}";

            if ( ImGui.TreeNodeEx( prefix != null ? $"{prefix}: {nodeName}" : nodeName, ImGuiTreeNodeFlags.DefaultOpen ) ) {
                foreach ( var entry in properties ) {
                    if ( entry.Key == "__type" || entry.Key == "__hashCode" ) continue;

                    RenderInspectorValue( entry.Key, entry.Value );
                }

                ImGui.TreePop();
            }
        }
        
        public void RenderInspectorValue ( string key, object value ) {
            if ( value is ICollection<object> ) {
                var list = value as ICollection<object>;

                if ( ImGui.TreeNodeEx( $"{ key }: { list.GetType().Name }({ list.Count } items)###{ list.GetHashCode() }", ImGuiTreeNodeFlags.DefaultOpen ) ) {
                    int i = 0;

                    foreach ( var obj in list ) {
                        RenderInspectorValue( i.ToString(), obj );

                        i++;
                    }

                    ImGui.TreePop();
                }
            } else if ( value is Dictionary<string, object> ) {
                var dictionary = value as Dictionary<string, object>;

                RenderInspector( dictionary, key );
            }  else {
                ImGui.BulletText( $"{key}: {value}"  );
            }
        }
        
        public Dictionary<string, object> CreateGrammarInspectorDictionary ( object obj ) {
            return CreateGrammarInspectorDictionary( obj, new HashSet<int>() );
        }

        public Dictionary<string, object> CreateGrammarInspectorDictionary ( object obj, HashSet<int> history ) {
            if ( history.Contains( obj.GetHashCode() ) ) return null;

            history.Add( obj.GetHashCode() );
            
            Type type = obj.GetType();

            var properties = new Dictionary<string, object>(){
                ["__type"] = type.Name,
                ["__hashCode"] = obj.GetHashCode()
            };

            foreach ( var prop in type.GetProperties() ) {
                if ( prop.GetIndexParameters().Length > 0 ) continue;
                
                var value = prop.GetValue( obj );

                properties[ prop.Name ] = CreateGrammarInspectorValue( value, history );
            }

            return properties;
        }

        public object CreateGrammarInspectorValue ( object value, HashSet<int> history ) {
            if ( value == null ) {
                return "<null>";
            } else if ( value is ICollection ) {
                return ( (ICollection)value ).OfType<object>().Select( obj => CreateGrammarInspectorValue( obj, history ) ).ToList();
            } else if ( value is ICollection<object> ) {
                return ( (ICollection<object>)value ).Select( obj => CreateGrammarInspectorValue( obj, history ) ).ToList();
            } else if ( value is string || value is int || value is float || value is bool || value is decimal || value is double || value is Enum ) {
                return value.ToString();
            } else {
                if ( history.Contains( value.GetHashCode() ) ) {
                    return "<circular>";
                } else {
                    return CreateGrammarInspectorDictionary( value, history );
                }
            }
        }

        public async Task SaveGrammar ( string content ) {
            await File.WriteAllTextAsync( @"./SoundPlayground/Parser/MusicParser.peg", content, System.Text.Encoding.UTF8 );
        }

        public void CompileGrammar () {
            grammarErrors = new List<string>();
            grammarWarnings = new List<string>();

            try {
                var compileResult = CompileManager.CompileString( grammarSource, "MusicParser.peg" );

                var dotnetCoreDirectory = Path.GetDirectoryName(typeof(object).GetTypeInfo().Assembly.Location);

                var compilation = CSharpCompilation.Create("LibraryName" + assemblyCount++)
                    .WithOptions(new CSharpCompilationOptions(OutputKind.DynamicallyLinkedLibrary))
                    .AddReferences(
                        MetadataReference.CreateFromFile(typeof(object).GetTypeInfo().Assembly.Location),
                        MetadataReference.CreateFromFile(typeof(GeneratedCodeAttribute).GetTypeInfo().Assembly.Location),
                        MetadataReference.CreateFromFile(typeof(MulticastDelegate).GetTypeInfo().Assembly.Location),
                        MetadataReference.CreateFromFile(typeof(IList<object>).GetTypeInfo().Assembly.Location),
                        MetadataReference.CreateFromFile(typeof(Cursor).GetTypeInfo().Assembly.Location),
                        MetadataReference.CreateFromFile(Assembly.GetExecutingAssembly().Location),
                        MetadataReference.CreateFromFile(Path.Combine(dotnetCoreDirectory, "netstandard.dll")),
                        MetadataReference.CreateFromFile(Path.Combine(dotnetCoreDirectory, "System.Runtime.dll")))
                    .AddSyntaxTrees(CSharpSyntaxTree.ParseText(compileResult.Code));
                
                var diagnostics = compilation.GetDiagnostics();

                grammarErrors = diagnostics.Where( d => d.Severity == DiagnosticSeverity.Error ).Select( d => d.ToString() ).ToList();
                grammarWarnings = diagnostics.Where( d => d.Severity != DiagnosticSeverity.Error ).Select( d => d.ToString() ).ToList();

                using (var ms = new MemoryStream())
                {
                    var emitResult = compilation.Emit(ms);
                    if (emitResult.Success)
                    {
                        ms.Seek(0, SeekOrigin.Begin);

                        var context = AssemblyLoadContext.Default;
                        var assembly = context.LoadFromStream( ms );

                        var parserType = assembly.GetType("SoundPlayground.Parser.MusicParser");

                        if ( parserType != null ) {
                            grammarParser = Activator.CreateInstance( parserType );
                        } else {
                            grammarErrors.Add( "Parser class not found" );
                        }

                    }
                }
            } catch ( Exception ex ) {
                grammarErrors.Add( ex.Message );
            }
        }

        public void ParseGrammarInput () {
            if ( grammarParser != null ) {
                try {
                    grammarTestError = null;

                    var obj = grammarParser.Parse( grammarTest, null );

                    grammarInspectorProperties = CreateGrammarInspectorDictionary( obj );

                } catch ( Exception ex ) {
                    grammarTestError = ex.Message;

                    grammarInspectorProperties = null;
                }
                
            }
        }

        public void DrawSplitter( float thickness, ref float containerSize, ref float size0, ref float size1, float minSize0 = 0, float minSize1 = 0, bool splitVertically = true )
        {
            float currentSize = splitVertically ? ImGui.GetContentRegionAvail().Y : ImGui.GetContentRegionAvail().X;

            if ( currentSize != containerSize ) {
                size0 = size0 * currentSize / containerSize;
                size1 = currentSize - size0;
                containerSize = currentSize;
            }

            Vector2 backupPos = ImGui.GetCursorPos();

            if ( splitVertically ) {
                ImGui.SetCursorPosY( backupPos.Y + size0 );
            } else {
                ImGui.SetCursorPosX( backupPos.X + size0 );
            }

            ImGui.PushStyleColor( ImGuiCol.Button, new Vector4( 0, 0, 0, 0 ) );
            ImGui.PushStyleColor( ImGuiCol.ButtonActive, new Vector4( 0, 0, 0, 0 ) );          // We don't draw while active/pressed because as we move the panes the splitter button will be 1 frame late
            ImGui.PushStyleColor( ImGuiCol.ButtonHovered, new Vector4( 0.6f, 0.6f, 0.6f, 0.10f ) );
            ImGui.Button( "##Splitter", new Vector2( !splitVertically ? thickness : -1.0f, splitVertically ? thickness : -1.0f ) );
            ImGui.PopStyleColor( 3 );

            ImGui.SetItemAllowOverlap(); // This is to allow having other buttons OVER our splitter. 

            if (ImGui.IsItemActive())
            {
                float mouseDelta = splitVertically ? ImGui.GetIO().MouseDelta.Y : ImGui.GetIO().MouseDelta.X;

                // Minimum pane size
                if ( mouseDelta < minSize0 - size0 ) {
                    mouseDelta = minSize0 - size0;
                }
                if ( mouseDelta > size1 - minSize1 ) {
                    mouseDelta = size1 - minSize1;
                }

                // Apply resize
                size0 += mouseDelta;
                size1 -= mouseDelta;
            }

            ImGui.SetCursorPos( backupPos );
        }
    
        public override async Task Load () {
            grammarSource = await File.ReadAllTextAsync( @"./SoundPlayground/Parser/MusicParser.peg" );

            grammarTest = code;
        }
    }
}
