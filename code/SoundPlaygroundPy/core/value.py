VALUE_KIND_MUSIC = 1

class Value:
    def __init__ ( self, kind, value ):
        self.kind = kind
        self.value = value
    
    def as_assignment ( self ):
        return self

    def get_events ( self, context ):
        if self.value != None and callable( getattr( self.value, "get_events", None ) ):
            for ev in self.value.get_events( context ):
                yield ev
