from .context import Context
from .voice import Voice
from typing import List

class Music:
    def __init__ ( self, notes = [] ):
        self.notes = notes

    def shared ( self ):
        return SharedMusic( self )

    def expand ( self, context : Context ):
        for note in self:
            if isinstance( note, Music ):
                for subnote in note.expand( context ):
                    yield subnote
            else:
                yield note

    def __iter__ ( self ):
        if self.notes and hasattr( self.notes, '__iter__' ):
            for note in self.notes:
                yield note

class SharedMusic(Music):
    def __init__ ( self, base_music : Music ):
        self.base_music : Music = base_music
        self.shared_music : SharedIterator = SharedIterator( iter( base_music ) )

    def shared ( self ):
        return self

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
        self.shared_music : SharedMusic = None

    def shared ( self ):
        return self
        
    def expand ( self, context : Context ):
        if self.shared_music == None:
            self.shared_music = SharedMusic( self.notes.eval( context.fork() ) )

        for note in self.shared_music.expand( context ):
            # if isinstance( note, Music ):
            #     for subnote in note.expand( context ):
            #         yield context.voice.revoice( subnote )
            # else:
                yield context.voice.revoice( note )
