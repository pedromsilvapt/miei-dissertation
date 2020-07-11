from typing import Any, Iterator, Optional, Tuple
from .node import Node
from .expressions import ExpressionNode
from musikla.core import Music, StackFrame


class MusicSequenceBase( Node ):
    def check_returns ( self ):
        return True

    def values ( self, context ):
        return iter(())

    def _check_stack_frame ( self, stack_frame : Optional[StackFrame], music_mode : bool = True ) -> bool:
        if not self.check_returns():
            return False

        if stack_frame is not None and stack_frame.returned:
            if music_mode and stack_frame.returned_value is not None:
                raise Exception( "A function that plays music cannot return value" )
            else:
                return True
        
        return False

    def _get_events ( self, context, stack_frame : Optional[StackFrame], iterator : Iterator[Any], pending_value = None ):
        if isinstance( pending_value, Music ):
            for event in pending_value.expand( context ):
                yield event

        if self._check_stack_frame( stack_frame ):
            return

        for value in iterator:
            if isinstance( value, Music ):
                for event in value.expand( context ):
                    yield event

            if self._check_stack_frame( stack_frame ):
                break

    def eval ( self, context ):
        value = None

        stack_frame : Optional[StackFrame] = context.symbols.lookup( 'stack_frame', container = 'stack' )

        iterator = iter( self.values( context ) )

        while True:
            try:
                value = next( iterator )

                if self._check_stack_frame( stack_frame, False ):
                    return stack_frame.returned_value

                if isinstance( value, Music ):
                    return Music( self._get_events( context, stack_frame, iterator, value ) )
            except StopIteration:
                break

        return value


class MusicNode( ExpressionNode ):
    def __init__ ( self, position : Tuple[int, int] = None ):
        super().__init__( position )
    
    def get_events ( self, context ):
        return iter( () )

    def eval ( self, context ):
        return Music( self.get_events( context ) )
