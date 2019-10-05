class Node():
    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)
