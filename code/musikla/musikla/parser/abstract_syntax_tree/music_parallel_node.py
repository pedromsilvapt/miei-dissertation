from collections import defaultdict
from musikla.parser.printer import CodePrinter
from typing import Dict, Generic, List, Tuple, TypeVar
from musikla.core import Music
from .music_node import MusicNode
from musikla.core import merge_sorted

T = TypeVar('T')

class Box( Generic[T] ):
    def __init__ ( self, value : T ):
        self.value : T = value
    
    def gset ( self, new_value : T ) -> T:
        old_value : T = self.value

        self.value = new_value

        return old_value
    
    def set ( self, value : T ):
        self.value = value

class MusicParallelNode( MusicNode ):
    def __init__ ( self, nodes, position : Tuple[int, int, int] = None ):
        super().__init__( position )
        
        self.expressions = nodes
    
    def to_source ( self, printer : CodePrinter ):
        for i in range( len( self.expressions ) ):
            if i > 0: printer.add_token( ' | ' )

            self.expressions[ i ].to_source( printer )

    def fork_and_get_events ( self, node, forks, context, staff_count : Box[int] ):
        forked = context.fork()

        forks.append( forked )

        value = node.eval( forked )

        def _update_staff ( events ):
            nonlocal staff_count
            
            staff_map : Dict[int, int] = defaultdict( lambda: staff_count.gset( staff_count.value + 1 ) )

            for event in events:
                if event.staff is not None:
                    event.staff = staff_map[ event.staff ]

                yield event

        if isinstance( value, Music ):
            return _update_staff( value.expand( forked ) )

        return iter(())

    def get_events ( self, context ):
        forks = []

        staff_count : Box[int] = Box( 0 )

        notes = map( lambda node: self.fork_and_get_events( node, forks, context, staff_count ), self.expressions )
        notes = merge_sorted( notes, lambda note: note.timestamp )

        try:
            for note in notes:
                yield note
        finally:
            context.join( *forks )
        