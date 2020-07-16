from musikla.parser.printer import CodePrinter
from typing import Tuple
from .node import Node
from musikla.core import Context
import inspect

class PythonNode( Node ):
    def __init__ ( self, code : str, is_expression : bool = False, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.code : str = code
        self.is_expression : bool = is_expression
        self.bytecode = compile( self.code, "<embedded python>", 'eval' if is_expression else 'exec' )
        self.hoisted : bool = not is_expression
    
    def to_source ( self, printer : CodePrinter ):
        if self.is_expression:
            printer.add_token( '@py' )
            with printer.block():
                printer.add_token( self.code )
        else:
            printer.add_token( '@python ' )
            printer.add_token( self.code )

    def get_auto_name ( self, val ):
        return val.__name__

    def create_export_decorator ( self, context : Context ):
        def export ( name : str = None ):
            nonlocal context

            def export_instance ( val ):
                nonlocal name, context

                if name is None:
                    name = self.get_auto_name( val )
                
                context.symbols.assign( name, val )

                return val
            
            return export_instance

        return export

    def __eval__ ( self, context : Context ):
        globals = {}

        if not self.is_expression:
            globals[ 'export' ] = self.create_export_decorator( context )
            locals = {}
        else:
            locals = PythonContext( context )
        

        return eval( self.bytecode, globals, locals )

class PythonContext:
    def __init__ ( self, context : Context ):
        self.context : Context = context
    
    def __getitem__ ( self, key ):
        return self.context.symbols.lookup( key, stop_on = self.context.symbols.prelude, default = KeyError(), raise_default = True )
    
    def __setitem__ ( self, key, value ):
        return self.context.symbols.assign( key, value )
    
    def __contains__ ( self, key ):
        try:
            self[ key ]

            return True
        except KeyError:
            return False

    def get(self, k):
        return self.__getitem__( k )

    def items( self ):
        return iter( () )
    def keys( self ):
        return iter( () )
    def values( self ):
        return iter( () )
    def __len__( self ):
        return 0

    # @overload
    # def get(self, k: _KT, default: Union[_VT_co, _T]) -> Union[_VT_co, _T]: ...
    # def items(self) -> AbstractSet[Tuple[_KT, _VT_co]]: ...
    # def keys(self) -> AbstractSet[_KT]: ...
    # def values(self) -> ValuesView[_VT_co]: ...
    # def __contains__(self, o: object) -> bool: ...