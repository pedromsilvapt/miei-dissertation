from .context import Context
from .voice import Voice
from .events import NoteEvent, MusicEvent
from .enumerable import merge_sorted
from typing import Any, Optional, List, Iterable, Tuple
from itertools import islice
from fractions import Fraction

class MusicBuffer:
    def __init__ ( self ):
        self.buffer : List[MusicEvent] = []
    
    def append ( self, event : MusicEvent ):
        l = len( self.buffer )

        for i in range( l + 1 ):
            if i == l:
                self.buffer.append( event )
            elif self.buffer[ i ].timestamp > event.timestamp:
                self.buffer.insert( i, event )
                
                break

    def collect ( self, time : int = None ):
        if time == None:
            for event in self.buffer:
                yield event
            
            self.buffer.clear()
        else:
            while self.buffer and self.buffer[ 0 ].timestamp <= time:
                yield self.buffer.pop( 0 )
            
    def __len__ ( self ):
        return len( self.buffer )
    
    def __bool__ ( self ):
        return bool( self.buffer )

class Music:
    @classmethod
    def parallel ( cls, tracks ):
        return cls( merge_sorted( tracks, lambda note: note.timestamp ) )

    def __init__ ( self, notes = [] ):
        self.notes = notes

    def len ( self, context : Context ) -> Fraction:
        range : Optional[Tuple[int, int]] = None
        
        for ev in self.expand( context ):
            if range is None:
                range = ( ev.timestamp, ev.end_timestamp )
            else:
                range = ( range[ 0 ], max( range[ 1 ], ev.end_timestamp ) )

        if range is None:
            return Fraction(0)
            
        start, end = range

        return context.voice.from_duration_absolute( end ) - context.voice.from_duration_absolute( start )

    def shared ( self ) -> 'SharedMusic':
        return SharedMusic( self )

    def expand ( self, context : Context ):
        for note in self:
            if isinstance( note, Music ):
                for subnote in note.expand( context ):
                    yield subnote
            else:
                yield note

    def transform ( self, transformer : Any, *args, **kargs ) -> 'MusicGen':
        return MusicGen( self, lambda it: transformer.iter( it, *args, **kargs ) )

    def slice ( self, start = None, end = None, time : bool = True, cut : bool = False ) -> 'Music':
        if time:
            if cut:
                if start is not None and end is not None:
                    def _map ( event, index, start ):
                        if event.timestamp < start or event.end_timestamp > end:
                            timestamp = max( event.timestamp, start )

                            diff = timestamp - event.timestamp

                            return event.clone( timestamp = timestamp, duration = min( event.duration - diff, end - timestamp ) )

                        return event
                    
                    return self.filter( lambda e, i, s: e.end_timestamp > start and e.timestamp < end ).map( _map )
                elif start is not None:
                    def _map ( event, index, start ):
                        if event.timestamp < start:
                            diff = start - event.timestamp

                            return event.clone( timestamp = start, duration = event.duration - diff )

                        return event

                    return self.filter( lambda e, i, s: e.end_timestamp > start ).map( _map )
                elif end is not None:
                    def _map ( event, index, start ):
                        if event.end_timestamp > end:
                            return event.clone( duration = end )

                        return event

                    return self.filter( lambda e, i, s: e.timestamp < end ).map( _map )
            else:
                if start is not None and end is not None:
                    return self.filter( lambda e, i, s: e.timestamp >= start and e.end_timestamp <= end )
                elif start is not None:
                    return self.filter( lambda e, i, s: e.timestamp >= start )
                elif end is not None:
                    return self.filter( lambda e, i, s: e.end_timestamp <= end )
        else:
            if start is not None and end is not None:
                return MusicGen( self, lambda it: islice( it, start, end ) )
            elif start is not None:
                return MusicGen( self, lambda it: islice( it, start ) )
            elif end is not None:
                return MusicGen( self, lambda it: islice( it, 0, end ) )

        return self

    def first_note ( self, context : Context ) -> Optional[NoteEvent]:
        it = self.expand( context )

        try:
            value = next( it )

            while not isinstance( value, NoteEvent ):
                value = next( it )

            return value
        except StopIteration:
            return None
    
    def last_note ( self, context : Context ):
        note = None

        for value in self.expand( context ):
            if isinstance( value, NoteEvent ):
                note = value
                
        return note

    def map ( self, mapper ) -> 'MusicMap':
        return MusicMap( self, mapper )

    def filter ( self, predicate ) -> 'MusicFilter':
        return MusicFilter( self, predicate )

    def __add__ ( self, other ):
        return self.map( lambda ev, i, s: ev + other )
    
    def __sub__ ( self, other ):
        return self.map( lambda ev, i, s: ev - other )

    def __iter__ ( self ):
        if self.notes and hasattr( self.notes, '__iter__' ):
            for note in self.notes:
                yield note

class SharedMusic(Music):
    def __init__ ( self, base_music : Iterable ):
        self.base_music : Iterable = base_music
        self.shared_music : SharedIterator = SharedIterator( iter( base_music ) )

    def shared ( self ):
        return self

    def peek ( self ) -> Optional[MusicEvent]:
        event : Optional[MusicEvent] = None

        for ev in self:
            event = ev
            break
        
        return event
        
    def peek_many ( self, count : int ) -> List[MusicEvent]:
        events : List[MusicEvent] = []

        i = 0

        for ev in self:
            events.append( ev )
            
            i += 1

            if i >= count:
                break
        
        return events
    

    def retime ( self, context, offset, note ):
        if offset is None:
            offset = context.cursor - note.timestamp
        
        note = note.clone( timestamp = note.timestamp + offset )

        context.cursor = note.end_timestamp

        return offset, note

    def expand ( self, context : Context ):
        offset = None

        for note in self.shared_music:
            if isinstance( note, Music ):
                for subnote in note.expand( context ):
                    offset, subnote = self.retime( context, offset, subnote )

                    yield subnote
            else:
                offset, note = self.retime( context, offset, note )

                yield note

    def __iter__ ( self ):
        for note in self.shared_music:
            yield note

class SharedIterator():
    def __init__ ( self, iterator ):
        self.iterator = iterator
        self.buffer : List = []
        self.stopped : bool = False

    def __iter__ ( self ):
        i : int = 0

        while not self.stopped or i < len( self.buffer ):
            if i < len( self.buffer ):
                i += 1

                yield self.buffer[ i - 1 ]
            else:
                try:
                    value = next( self.iterator )

                    self.buffer.append( value )

                    i += 1

                    yield value
                except StopIteration:
                    self.stopped = True

    # def get_events ( self, context ):
    #     forked = self.context.fork( cursor = context.cursor )

    #     for event in self.node.eval( forked ):
    #         context.join( forked )
            
    #         yield event

    #     context.join( forked )
        
class TemplateMusic(Music):
    def __init__ ( self, notes = [] ):
        super().__init__( notes )
        self.shared_music : Optional[SharedMusic] = None

    def shared ( self ):
        return self
        
    def expand ( self, context : Context ):
        if self.shared_music == None:
            self.shared_music = SharedMusic( self.notes.eval( context.fork() ) )

        for note in self.shared_music.expand( context ):
            yield context.voice.revoice( note )

class MusicGen(Music):
    def __init__ ( self, base : Music, mapper ):
        super().__init__( [] )

        self.base : Music = base
        self.mapper = mapper

    def expand ( self, context : Context ):
        for event in self.mapper( self.base.expand( context ) ):
            yield event

    def __iter__ ( self ):
        for event in self.mapper( self.base ):
            yield event

class MusicMap(Music):
    def __init__ ( self, base : Music, mapper ):
        super().__init__( [] )

        self.base : Music = base
        self.mapper = mapper

    def expand ( self, context : Context ):
        start_time = 0
        index = 0

        for event in self.base.expand( context ):
            if index == 0:
                start_time = event.timestamp
            
            yield self.mapper( event, index, start_time )

            index += 1

    def __iter__ ( self ):
        start_time = 0
        index = 0

        for event in self.base:
            if index == 0:
                start_time = event.timestamp
            
            yield self.mapper( event, index, start_time )

            index += 1

class MusicFilter(Music):
    def __init__ ( self, base : Music, predicate ):
        super().__init__( [] )

        self.base : Music = base
        self.predicate = predicate

    def expand ( self, context : Context ):
        start_time = 0
        index = 0

        for event in self.base.expand( context ):
            if index == 0:
                start_time = event.timestamp
            
            if self.predicate( event, index, start_time ):
                yield event

            index += 1

    def __iter__ ( self ):
        start_time = 0
        index = 0

        for event in self.base:
            if index == 0:
                start_time = event.timestamp
            
            if self.predicate( event, index, start_time ):
                yield event

            index += 1
