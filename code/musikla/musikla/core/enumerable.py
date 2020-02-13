class IterCursor ():
    def __init__ ( self, iterable ):
        self.iterator = iter( iterable )
        self.ended = False
        self.current = None
        
    def move_next ( self ):
        try:
            self.current = next( self.iterator )
            
            return True
        except StopIteration:
            self.current = None

            return False

    def close ( self ):
        if callable( getattr( self.iterator, 'close', None ) ):
            self.iterator.close()


def merge_sorted ( items, order = lambda x: x ):
    items = map( lambda en: IterCursor( en ), items )
    items = filter( lambda en: en.move_next(), items )
    items = map( lambda enumerator: ( order( enumerator.current ), enumerator ), items )
    items = list( sorted( items, key = lambda en: en[ 0 ] ) )
    
    try:
        while len( items ) > 0:
            next = items[ 0 ]

            yield next[ 1 ].current

            del items[ 0 ]

            if next[ 1 ].move_next():
                value = order( next[ 1 ].current )

                l = len( items )

                for i in range( l + 1 ):
                    if i == l or value < items[ i ][ 0 ]:
                        items.insert( i, ( value, next[ 1 ] ) )

                        break
                
            else: next[ 1 ].close()
    finally:
        for en in items: en[ 1 ].close()

        items = None

__all__ = []
