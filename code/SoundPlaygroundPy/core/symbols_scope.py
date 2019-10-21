class SymbolsScope:
    def __init__ ( self, parent = None ):
        self.parent = parent
        self.symbols = dict()

    def lookup ( self, name, container = "" ):
        if container in self.symbols and name in self.symbols[ container ]:
            return self.symbols[ container ][ name ]
        
        if self.parent != None:
            return self.parent.lookup( name, container = container )
        
        return None

    def assign ( self, name, value, container = "" ):
        if container not in self.symbols:
            self.symbols[ container ] = dict()

        self.symbols[ container ][ name ] = value

    def lookup_instrument ( self, name ):
        return self.lookup( name, container = "instruments" )

    def assign_instrument ( self, instrument ):
        self.assign( instrument.name, instrument, container = "instruments" )
        
        return instrument

    def lookup_internal ( self, name ):
        return self.lookup( name, container = "internal" )

    def assign_internal ( self, name, value ):
        self.assign( name, value, container = "internal" )

    def fork ( self ):
        return SymbolsScope( self )

    def unref ( self ):
        for name, value in self.symbols:
            if callable( getattr( value, 'unref', None ) ):
                value.unref()
