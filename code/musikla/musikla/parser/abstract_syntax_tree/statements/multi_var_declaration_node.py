from musikla.parser.printer import CodePrinter
from typing import Any, Optional, Tuple, List
from .statement_node import StatementNode
from ..node import Node
from musikla.core import Value, Context

class MultiVariableDeclarationStatementNode( StatementNode ):
    def __init__ ( self, left : List[Node], right : Node, operator : Optional[str] = None, local : bool = False, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.left : Any = left

        self.right : Any = right
        self.operator : Optional[str] = operator
        self.local : bool = local

        for op in self.left:
            if self.operator is None and not hasattr( op, 'assign' ):
                raise BaseException( f"Left hand side \"{CodePrinter().print(op)}\" cannot be used in an attribution" )
            elif self.operator is not None and not hasattr( op, 'lookup_assign' ):
                raise BaseException( f"Left hand side \"{CodePrinter().print(op)}\" cannot be used in an attribution" )

    def __eval__ ( self, context : Context ):
        val = Value.assignment( self.right.eval( context.fork( cursor = 0 ) ) )

        for i, op in enumerate( self.left ):
            if self.operator is None or self.operator == "":
                op.assign( context, val[ i ], local = self.local )
            else:
                def _set ( value ):
                    nonlocal val

                    if self.operator == '*': value *= val[ i ]
                    elif self.operator == '/': value /= val[ i ]
                    elif self.operator == '+': value += val[ i ]
                    elif self.operator == '-': value -= val[ i ]
                    elif self.operator == '&': value &= val[ i ]
                    elif self.operator == '|': value |= val[ i ]
                    else: raise Exception( "Invalid operator: " + self.operator )

                    return value

                op.lookup_assign( context, _set, local = self.local )

        return None

    def to_source ( self, printer : CodePrinter ):
        for i, op in enumerate( self.to_source ):
            if i > 0:
                printer.add_token( ", " )

            op.to_source( printer )

        printer.add_token( f" { self.operator if self.operator is not None else '' }= " )
        
        self.right.to_source( printer )
