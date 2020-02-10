from musikla.core import Context, Value

class Node():
    def __init__ ( self, position : (int, int) = None ):
        self.position : int = position

    def eval ( self, context : Context, assignment : bool = False ) -> Value:
        pass

    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)
