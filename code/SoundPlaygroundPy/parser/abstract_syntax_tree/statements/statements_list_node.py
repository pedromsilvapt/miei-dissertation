from .statement_node import StatementNode
from core import Value, VALUE_KIND_MUSIC

class StatementsListNode( StatementNode ):
    def __init__ ( self, nodes, position : (int, int) = None ):
        super().__init__( position )

        self.statements = nodes

    def get_events ( self, context, value, index ):
        for event in value:
            yield event

        for node in self.statements[ index: ]:
            value = node.eval( context )

            # print( len( self.statements ), index, value.kind if value != None else None )

            if value and value.kind == VALUE_KIND_MUSIC:
                for event in value:
                    yield event

            index += 1
    
    def eval ( self, context, assignment = False ):
        i = 0

        for node in self.statements:
            value = node.eval( context )
            # print( len( self.statements ), i, value.kind if value != None else None )

            if value and value.kind == VALUE_KIND_MUSIC:
                return Value( VALUE_KIND_MUSIC, self.get_events( context, value, i + 1 ) )

            i += 1

        return value
