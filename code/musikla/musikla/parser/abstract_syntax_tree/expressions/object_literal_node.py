from .expression_node import ExpressionNode
from musikla.core import Value
from typing import List, Tuple

class Object(dict):
    def __init__ ( self, pairs = [] ):
        super().__init__( pairs )
    
    def has ( self, key ):
        return key in self
    
    def get ( self, key, default = None ):
        if key in self:
            return self[ key ]

        return default
        
    def set ( self, key, value ):
        self[ key ] = value

        return self
        
    def delete ( self, key ):
        del self[ key ]

    def __delattr__ ( self, key ):
        del self[ key ]

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
