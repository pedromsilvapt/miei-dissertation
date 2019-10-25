from typing import Hashable

class Pointer:
    def __init__ ( self, scope, name ):
        self.scope = scope
        self.name = name

class SymbolsScope:
    def __init__ ( self, parent = None ):
        self.parent = parent
        self.symbols = dict()

    def using ( self, name : Hashable, alias : str = None, container : str = "" ):
        scope = self

        while scope != None:
            value = scope.lookup( name, container = container, recursive = False, follow_pointers = False )

            if value != None:
                if isinstance( value, Pointer ):
                    scope = value.scope

                break

            scope = scope.parent

        if scope == None:
            raise BaseException( f"Trying to use global undefined symbol { name }" )

        self.assign( alias or name, Pointer( scope, name ), container = container )

    def lookup ( self, name : Hashable, container : str = "", recursive : bool = True, follow_pointers : bool = True, default = None ):
        if container in self.symbols and name in self.symbols[ container ]:
            value = self.symbols[ container ][ name ]

            if follow_pointers and isinstance( value, Pointer ):
                return pointer.scope.lookup( pointer.name, container = container )

            return value
        
        if recursive and self.parent != None:
            return self.parent.lookup( name, container = container, follow_pointers = follow_pointers, default = default )
        
        return default

    def assign ( self, name : Hashable, value, container = "", follow_pointers : bool = True ):
        if follow_pointers:
            existing_value = self.lookup( name, container = container, recursive = False, follow_pointers = False )

            if existing_value != None and isinstance( existing_value, Pointer ):
                existing_value.scope.assign( existing_value.name, value, container = container )

                return

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
