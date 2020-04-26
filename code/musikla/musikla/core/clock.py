import time
from typing import Optional

class Clock():
    @staticmethod
    def epoch ():
        return Clock( auto_start = 0 )

    @staticmethod
    def _get_global_milliseconds () -> int:
        return int( round( time.time() * 1000 ) )

    def __init__ ( self, auto_start = True, start_time : int = None ):
        self.start_time : Optional[int] = None
        self.auto_start : bool = auto_start

    @property
    def started ( self ):
        return self.start_time is not None

    def start ( self ):
        self.start_time = self._get_global_milliseconds()

        return self

    def reset ( self ):
        self.start_time = None

        return self

    def elapsed ( self ):
        if self.auto_start and self.start_time is None:
            self.start()

        if self.start_time is None:
            return self._get_global_milliseconds()
        else:
            return self._get_global_milliseconds() - self.start_time
