from core import Context, Library, CallableValue
from core import Value, VALUE_KIND_MUSIC, Note
from parser.abstract_syntax_tree.expressions import VariableExpressionNode

def function_arpeggio ( context : Context, chord, pattern = None ):
    forked = context.fork()

    value = chord.eval( forked )

    if not value.is_music:
        raise BaseException( "Expected musical notes for an arpeggio" )

    baseline : int = None
    
    for event in value:
        if isinstance( event, Note ):
            if baseline == None:
                baseline = event.timestamp
            else:
                event.timestamp = baseline

            baseline += event.duration

        yield event

    if baseline != None:
        context.cursor = baseline
            


class MusicLibrary(Library):
    def on_link ( self ):
        context : Context = self.context

        context.symbols.assign( "arpeggio", CallableValue( function_arpeggio ) )

