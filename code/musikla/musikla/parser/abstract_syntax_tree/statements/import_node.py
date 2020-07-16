from musikla.parser.printer import CodePrinter
from typing import Tuple
from musikla.core import Context
from .statement_node import StatementNode

class ImportStatementNode( StatementNode ):
    def __init__ ( self, module_name : str, local : bool, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.module_name : str = module_name
        self.local : bool = local

    def __eval__ ( self, context : Context ):
        module_path = context.script.resolve_import( context.symbols.lookup( '__file__' ), self.module_name, local = self.local )
        
        context.script.import_module( context, module_path )

        return None

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( 'import ' )

        if self.local:
            printer.add_token( f'"{self.module_name}"' )
        else:
            printer.add_token( self.module_name )
