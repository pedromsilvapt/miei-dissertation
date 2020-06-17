from typing import Hashable, Optional, Set

class Pointer:
    def __init__ ( self, scope, name ):
        self.scope = scope
        self.name = name

    def __str__ ( self ):
        return f"Pointer@{ id( self.scope ) }\{ self.name }"

"""
A note about the terminology here:
    - Opaque symbol scopes are scopes that, when assigned to, will always default to storing the value in themselves.
      This means that if a parent scope has a symbol with the same name, then it will be shadowed by the new one.
      If the intention is to use the parent's symbol, then a pointer needs to be created first (with the `using` method)
    - Transparent symbol scopes, on the other hand, before assigning a new symbol, will perform a shallow search up their
      scope tree for a symbol with the same name, and if found, create a pointer automatically.
    - Shallow searches are recursive searches that stop at the first opaque symbol scope they find.
"""

class ValueNotFound:
    pass

class SymbolsScope:
    def __init__ ( self, parent = None, opaque : bool = True ):
        self.parent : SymbolsScope = parent
        self.symbols : dict = dict()
        self.opaque : bool = opaque

    @property
    def root ( self ) -> 'SymbolsScope':
        scope : SymbolsScope = self

        while scope.parent is not None:
            scope = scope.parent
        
        return scope

    @property
    def prelude ( self ) -> Optional['SymbolsScope']:
        scope : SymbolsScope = self

        while scope is not None:
            if scope.lookup( "is_prelude", 'internal', recursive = False ):
                return scope
            
            scope = scope.parent
        
        return None

    def pointer ( self, name : Hashable, container : str = "", shallow : bool = False ) -> Pointer:
        scope : SymbolsScope = self

        while scope != None:
            value = scope.lookup( name, container = container, recursive = False, follow_pointers = False, default = ValueNotFound )

            if value != ValueNotFound:
                if isinstance( value, Pointer ):
                    scope = value.scope
                    name = value.name

                break

            if shallow and scope.opaque:
                scope = None
            else:
                scope = scope.parent

        if scope == None:
            return None
        else:
            return Pointer( scope, name )

    def using ( self, name : Hashable, alias : str = None, container : str = "", shallow : bool = False, soft : bool = False ) -> 'SymbolsScope':
        if isinstance( name, Pointer ):
            pointer = name
            name = pointer.name
        elif name != None and self.parent != None:
            pointer = self.parent.pointer( name, container = container, shallow = shallow )
        else:
            pointer = None
        
        if pointer == None and not soft:
            raise BaseException( f"Trying to use global undefined symbol { name }" )
        elif pointer != None:
            self.assign( alias or name, pointer, container = container, local = True )
        
        return pointer.scope if pointer != None else None

    def enumerate ( self, prefix : str = None, limit : int = None, ignore : Set = None, container : str = "", local : bool = False ):
        if ignore is None:
            ignore = set()

        count = 0

        if container in self.symbols:
            for key, value in self.symbols[ container ].items():
                if limit is not None:
                    if count >= limit:
                        return
                    else:
                        count += 1
                
                if key in ignore:
                    continue

                if prefix is not None and not key.startswith( prefix ):
                    continue

                ignore.add( key )

                yield key, value

        
        if not local and self.parent is not None:
            if limit is not None:
                limit -= count

            for key, value in self.parent.enumerate( prefix = prefix, limit = limit, ignore = ignore, container = container ):
                yield key, value


    def lookup ( self, name : Hashable, container : str = "", recursive : bool = True, follow_pointers : bool = True, default = None, raise_default : bool = False, stop_on : Optional['SymbolsScope'] = None ):
        if stop_on is None or self != stop_on:
            if container in self.symbols and name in self.symbols[ container ]:
                value = self.symbols[ container ][ name ]

                if follow_pointers and isinstance( value, Pointer ):
                    return value.scope.lookup( value.name, container = container )

                return value
            
            if recursive and self.parent != None:
                return self.parent.lookup( name, container = container, follow_pointers = follow_pointers, default = default, raise_default = raise_default, stop_on = stop_on )
        
        if raise_default:
            raise default
        else:
            return default

    def assign ( self, name : Hashable, value, container = "", follow_pointers : bool = True, local : bool = True ):
        if container not in self.symbols:
            self.symbols[ container ] = dict()

        if name not in self.symbols[ container ]:
            if not local and not self.opaque:
                self.using( name, container = container, shallow = True, soft = True )

        if follow_pointers:
            existing_value = self.lookup( name, container = container, recursive = False, follow_pointers = False )

            if existing_value != None and isinstance( existing_value, Pointer ):
                existing_value.scope.assign( existing_value.name, value, container = container )

                return

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

    def fork ( self, opaque : bool = True ):
        return SymbolsScope( self, opaque )

    def import_from ( self, scope : 'SymbolsScope', local : bool = True ):
        for key, value in scope.enumerate( local = local ):
            # Treat symbols that start with an underscore as private
            if not key.startswith( "_" ):
                self.assign( key, value, local = True )

    def unref ( self ):
        for name, value in self.symbols:
            if callable( getattr( value, 'unref', None ) ):
                value.unref()

class Ref:
    def __init__ ( self, pointer : Pointer, container : str = '' ):
        self.pointer : Pointer = pointer
        self.container : str = container

    def get ( self ):
        return self.pointer.scope.lookup( self.pointer.name, container = self.container )

    def set ( self, value ):
        self.pointer.scope.assign( self.pointer.name, value, container = self.container )
