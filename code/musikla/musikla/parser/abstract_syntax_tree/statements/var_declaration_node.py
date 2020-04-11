from musikla.parser.printer import CodePrinter
from typing import Optional, Tuple
from .statement_node import StatementNode
from musikla.core import Value, Context

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, name, expression, operator : Optional[str] = None, local : bool = False, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.name : str = name
        self.expression = expression
        self.operator : Optional[str] = operator
        self.local : bool = local

    def eval ( self, context : Context ):
        val = Value.assignment( self.expression.eval( context.fork() ) )

        if self.operator is None:
            context.symbols.assign( self.name, val, local = self.local )
        else:
            value = context.symbols.lookup( self.name, recursive = not self.local )

            if self.operator == '*': value *= val
            elif self.operator == '/': value /= val
            elif self.operator == '+': value += val
            elif self.operator == '-': value -= val
            elif self.operator == '&': value &= val
            elif self.operator == '|': value |= val
            else: raise Exception( "Invalid operator: " + self.operator )

            context.symbols.assign( self.name, value, local = self.local )

        return None

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( f"${ self.name } { self.operator if self.operator is not None else '' }= " )
        
        self.expression.to_source( printer )
