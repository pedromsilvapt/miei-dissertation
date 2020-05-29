from typing import Generator, Tuple, AsyncGenerator, Union

class Transformer():
    @staticmethod
    def pipeline2 ( *transformers : 'Transformer' ) -> Tuple['Transformer', 'Transformer']:
        if not transformers:
            raise Exception( "Pipeline cannot be empty" )

        first = transformers[ 0 ]
        latest = first

        for transformer in transformers[ 1: ]:
            latest = latest.pipe_to( transformer )

        return first, latest
    
    @staticmethod
    def pipeline ( *transformers : 'Transformer' ) -> 'Transformer':
        return Transformer.pipeline2( *transformers )[ 0 ]

    @classmethod
    def subscriber ( cls, on_value, on_end = None ):
        transformer = cls()

        transformer.subscribe( on_value, on_end )

        return transformer


    def __init__ ( self ):
        self.subscriptions = []
        self.generator : Generator = self.transform()
        self.input_ended : bool = False
        self.output_ended : bool = False

        self.generator.send( None )

    def transform ( self ):
        while True:
            ended, event = yield

            if ended: break

            self.add_output( event )

    def add_output ( self, item ):
        self._notify_value( item )

    def end_output ( self ):
        if not self.output_ended:
            self.output_ended = True

            self._notify_end()

    def add_input ( self, item ):
        try:
            result = self.generator.send( ( False, item ) )
            
            if result != None:
                self.add_output( result )
        except StopIteration:
            self.end_output()

    def end_input ( self ):
        if not self.input_ended:
            self.input_ended = True

            while not self.output_ended:
                try:
                    result = self.generator.send( ( True, None ) )
                    
                    if result != None:
                        self.add_output( result )
                except StopIteration:
                    self.end_output()

                    break

    def _notify_value ( self, value ):
        for on_value, _ in self.subscriptions:
            if on_value != None: on_value( value )
        
    def _notify_end ( self ):
        for _, on_end in self.subscriptions:
            if on_end != None: on_end()

    def subscribe ( self, on_value, on_end = None ):
        self.subscriptions.append( ( on_value, on_end ) )

    def pipe_to ( self, transformer : 'Transformer', return_self : bool = False ):
        self.subscribe( lambda value: transformer.add_input( value ), lambda: transformer.end_input() )

        if return_self:
            return self
        else:
            return transformer

    @classmethod
    def iter ( cls, it, *args, **kargs ):
        """
        Receives a sync iterable and processes it with this transformer,
        returning the resulting sync iterator
        """
        inst : 'Transformer' = cls( *args, **kargs )

        def generator ():
            nonlocal inst, it

            it = iter( it )

            buffer = []

            inst.subscribe( lambda v: buffer.append( v ) )

            while True:
                for item in buffer: yield item

                buffer.clear()

                try:
                    item = next( it )

                    inst.add_input( item )

                    if inst.output_ended:
                        if hasattr( it, 'close' ) and callable( it.close ):
                            it.close()
                except StopIteration:
                    inst.end_input()

                    break

            for item in buffer: yield item

            buffer.clear()

        return generator()

    @classmethod
    def aiter ( cls, it, *args, **kargs ):
        """
        Receives either a sync or async iterable and processes it with this transformer,
        returning the resulting async iterator
        """
        inst : 'Transformer' = cls( *args, **kargs )

        async def generator ():
            nonlocal inst, it

            if not hasattr( it, '__aiter__' ) and hasattr( it, '__iter__' ):
                it = iter_to_aiter( it )

            it = it.__aiter__()

            buffer = []

            inst.subscribe( lambda v: buffer.append( v ) )

            while True:
                for item in buffer: yield item
                
                buffer.clear()

                try:
                    inst.add_input( await it.__anext__() )
                    
                    if inst.output_ended:
                        if hasattr( it, 'aclose' ) and callable( it.aclose ):
                            await it.aclose()
                except StopAsyncIteration:
                    inst.end_input()
                    break

            for item in buffer: yield item

            buffer.clear()

        return generator()

async def iter_to_aiter ( it ):
    for item in it:
        yield item
