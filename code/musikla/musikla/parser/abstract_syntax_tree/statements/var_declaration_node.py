from musikla.parser.printer import CodePrinter
from typing import Any, Optional, Tuple, Union
from .statement_node import StatementNode
from ..expressions.variable_expression_node import VariableExpressionNode
from ..node import Node
from musikla.core import Value, Context

class VariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, left : Union[Node, str], right : Node, operator : Optional[str] = None, local : bool = False, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        if type( left ) is str:
            self.left : Any = VariableExpressionNode( left )
        else:
            self.left : Any = left

        self.right : Any = right
        self.operator : Optional[str] = operator
        self.local : bool = local

        if self.operator is None and not hasattr( self.left, 'assign' ):
            raise BaseException( f"Left hand side \"{CodePrinter().print(self.left)}\" cannot be used in an attribution" )
        elif self.operator is not None and not hasattr( self.left, 'lookup_assign' ):
            raise BaseException( f"Left hand side \"{CodePrinter().print(self.left)}\" cannot be used in an attribution" )

    def __eval__ ( self, context : Context ):
        val = Value.assignment( self.right.eval( context.fork( cursor = 0 ) ) )

        if self.operator is None or self.operator == "":
            self.left.assign( context, val, local = self.local )
        else:
            def _set ( value ):
                nonlocal val

                # value = context.symbols.lookup( self.name, recursive = not self.local )
                if self.operator == '*': value *= val
                elif self.operator == '/': value /= val
                elif self.operator == '+': value += val
                elif self.operator == '-': value -= val
                elif self.operator == '&': value &= val
                elif self.operator == '|': value |= val
                else: raise Exception( "Invalid operator: " + self.operator )

                return value

            self.left.lookup_assign( context, _set, local = self.local )

        return None

    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( f" { self.operator if self.operator is not None else '' }= " )
        
        self.right.to_source( printer )
