class SymbolsScope:
    def __init__ ( self, parent = None ):
        self.parent = parent
        self.symbols = dict()
        self.instruments = dict()

    def lookup_instrument ( self, name ):
        if name in self.instruments:
            return self.instruments[ name ]
        
        if self.parent != None:
            return self.parent.lookup_instrument( name )
        
        return None

    def assign_instrument ( self, instrument ):
        self.instruments[ instrument.name ] = instrument

        return instrument

    def lookup ( self, name ):
        if name in self.symbols:
            return self.symbols[ name ]
        
        if self.parent != None:
            return self.parent.lookup( name )
        
        return None

    def assign ( self, name, value ):
        self.symbols[ name ] = value

    def fork ( self ):
        return SymbolScope( self )

    def unref ( self ):
        for name, value in self.symbols:
            if callable( getattr( value, 'unref', None ) ):
                value.unref()
