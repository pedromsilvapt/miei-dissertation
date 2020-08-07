from musikla.parser.printer import CodePrinter
from typing import Tuple
from .expression_node import ExpressionNode

class StringLiteralNode( ExpressionNode ):
    def __init__ ( self, value, position : Tuple[int, int, int] = None ):
        super().__init__( position )

        self.value = value

    def __eval__ ( self, context, assignment : bool = False ):
        return self.value

    def to_source ( self, printer : CodePrinter ):
        printer.add_token( "'" + self.value + "'" )

    @staticmethod
    def escaped ( value, quote : str = '"' ) -> 'StringLiteralNode':
        escaped_str = None

        l = len( value )
        v = None
        rv = None
        skip = False
        cursor = 0

        for i in range( l ):
            if skip:
                skip = False

                continue

            if value[ i ] == "\\":
                if l > i + 1:
                    v = value[ i + 1 ]
                    rv = None

                    if v == "\\":
                        rv = "\\"
                    elif v == "n":
                        rv = "\n"
                    elif v == "r":
                        rv = "\r"
                    elif v == "t":
                        rv = "\t"
                    elif v == quote:
                        rv = quote
                    
                    if rv is not None:
                        skip = True

                        if escaped_str is None:
                            escaped_str = value[ :i ] + rv
                        else:
                            escaped_str += value[ cursor:i ] + rv
                        
                        cursor = i + 2

        if escaped_str is None:
            escaped_str = value
        else:
            escaped_str += value[cursor:]
        
        return escaped_str
