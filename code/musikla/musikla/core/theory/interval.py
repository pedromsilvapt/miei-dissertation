class Interval:
    @staticmethod
    def octaves_to_semitones ( octaves : int ) -> int:
        return ( octaves * 12 )

    def __init__ ( self, semitones : int = 0, octaves : int = 0 ):
        self.full_semitones : int = semitones + Interval.octaves_to_semitones( octaves )
    
    @property
    def semitones ( self ) -> int:
        return self.full_semitones % 12

    @property
    def octaves ( self ) -> int:
        return self.full_semitones // 12

    def __int__ ( self ):
        return self.full_semitones

    def __add__ ( self, interval ):
        if interval is None:
            return

        if type( interval ) == int:
            return Interval( self.full_semitones + interval )
        elif isinstance( interval, Interval ):
            return Interval( self.full_semitones + interval.full_semitones )

    def __sub__ ( self, interval ):
        if interval is None:
            return

        if type( interval ) == int:
            return Interval( self.full_semitones - interval )
        elif isinstance( interval, Interval ):
            return Interval( self.full_semitones - interval.full_semitones )