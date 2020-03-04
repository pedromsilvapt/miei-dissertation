from .expression_node import ExpressionNode
from musikla.core import Value
from typing import List, Tuple

class Object(dict):
    def __init__ ( self, pairs = [] ):
        super().__init__( pairs )
    
    def __getattr__ ( self, key ):
        return self[ key ]

    def __setattr__ ( self, key, value ):
        self[ key ] = value

class ObjectLiteralNode( ExpressionNode ):
    def __init__ ( self, values : List[Tuple[str, ExpressionNode]], position : (int, int) = None ):
        super().__init__( position )

        self.values : List[Tuple[str, ExpressionNode]] = values

    def eval ( self, context ):
        return Object( [ ( key, Value.assignment( Value.eval( context.fork(), node ) ) ) for key, node in self.values ] )
