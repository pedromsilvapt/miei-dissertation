from sys import exc_info
from musikla.parser.printer import CodePrinter
from typing import Any, Optional, Tuple
from musikla.core import Context 
from ..error_reporter import ErrorReporter

class Node():
    def __init__ ( self, position : Tuple[int, int, int] = None ):
        self.position : Optional[Tuple[int, int, int]] = position
        self.hoisted : bool = False

    def __eval__ ( self, context : Context ) -> Any:
        return None
    
    def eval ( self, context : Context ) -> Any:
        try:
            return self.__eval__( context )
        except:
            _, err, _ = exc_info()

            if err is not None:
                if isinstance( err, MusiklaExecutionError ):
                    if err.position is None:
                        err.position = self.position
                    
                    raise err from None
                else:
                    raise MusiklaExecutionError( err, self.position )

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( f"<{self.__class__.__name__}>" )
        
    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)

class ValueNode(Node):
    def __init__ ( self, value : Any ):
        self.value : Any = value
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( "<VALUE>" )

    def __eval__ ( self, context : Context ):
        return self.value

class MusiklaExecutionError(Exception):
    def __init__ ( self, base_exception : BaseException, position : Tuple[int, int, int] = None ):
        super().__init__()

        self.position : Optional[Tuple[int, int, int]] = position
        self.base_exception : BaseException = base_exception
        self.file : Optional[str] = None
        self.content : Optional[str] = None
        self.reporter : Optional[ErrorReporter] = None
    
    def create_reporter ( self, file : str = None, content : str = None ):
        self.content = content
        self.file = file

        if self.position is not None and self.content is not None and self.file is not None:
            _, start, end = self.position
            
            self.reporter = ErrorReporter( "EvalError", str( self.base_exception ), self.content, ( start, end ), self.file )
    
    def __str__ ( self ):
        if self.reporter is not None:
            return str( self.reporter )
        
        return str( self.base_exception )
