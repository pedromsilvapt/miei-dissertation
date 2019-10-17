class Node():
    def eval ( self, context, assignment : bool = False ):
        pass

    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)
