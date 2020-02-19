import time

class Clock():
    @staticmethod
    def _get_global_milliseconds () -> int:
        return int( round( time.time() * 1000 ) )

    def __init__ ( self, auto_start = True ):
        self.start_time = None
        self.auto_start : bool = auto_start

    def start ( self ):
        self.start_time = self._get_global_milliseconds()

    def reset ( self ):
        self.start_time = None

    def elapsed ( self ):
        if self.auto_start and self.start_time is None:
            self.start()

        if self.start_time is None:
            return self._get_global_milliseconds()
        else:
            return self._get_global_milliseconds() - self.start_time
