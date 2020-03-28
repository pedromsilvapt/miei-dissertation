from typing import Any, Optional, Tuple
from .statement_node import StatementNode
from musikla.core import Music, StackFrame, Context

class StatementsListNode( StatementNode ):
    def __init__ ( self, nodes, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.statements = nodes

    def get_events ( self, context : Context, stack_frame : Optional[StackFrame], value, index ):
        for event in value:
            yield event

        for node in self.statements[ index: ]:
            value = node.eval( context )

            if stack_frame is not None and stack_frame.returned:
                if stack_frame.returned_value is not None:
                    raise Exception( "A function that plays music cannot return value" )
                else:
                    break

            if isinstance( value, Music ):
                for event in value:
                    yield event

            index += 1

    # def _get_stack_frame ( self, context ) -> StackFrame:
    #     if self.create_stack_frame:
    #         stack_frame = StackFrame()

    #         context.symbols.assign( 'stack_frame', stack_frame, container = 'stack' )

    #         return stack_frame
    #     else:
    #         return 


    def eval ( self, context : Context ):
        i = 0

        value = None

        stack_frame : Optional[StackFrame] = context.symbols.lookup( 'stack_frame', container = 'stack' )

        for node in self.statements:
            value = node.eval( context )

            if stack_frame is not None and stack_frame.returned:
                return stack_frame.returned_value

            if isinstance( value, Music ):
                return Music( self.get_events( context, stack_frame, value, i + 1 ) )

            i += 1

        return value
