from typing import Tuple
from .statement_node import StatementNode
from musikla.core import Music

class StatementsListNode( StatementNode ):
    def __init__ ( self, nodes, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.statements = nodes

    def get_events ( self, context, value, index ):
        for event in value:
            yield event

        for node in self.statements[ index: ]:
            value = node.eval( context )

            if isinstance( value, Music ):
                for event in value:
                    yield event

            index += 1
    
    def eval ( self, context ):
        i = 0

        value = None

        for node in self.statements:
            value = node.eval( context )

            if isinstance( value, Music ):
                return Music( self.get_events( context, value, i + 1 ) )

            i += 1

        return value
