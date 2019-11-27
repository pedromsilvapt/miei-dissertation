from ..node import Node
from .expression_node import ExpressionNode
from core import Value, Music
from typing import Union

class BinaryOperatorNode( ExpressionNode ):
    def __init__ ( self, left : Node, right : Node, position : (int, int) = None ):
        super().__init__( position )

        self.left : Node = left
        self.right : Node = right

    def eval ( self, context ):
        return self.value

class PlusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value + right_value

class MinusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value - right_value
    
class MultBinaryOperatorNode(BinaryOperatorNode):
    def get_events ( self, context, events : Music, count : int ):
        if count == 0: return

        for event in events:
            yield event

        for i in range( 1, count ):
            events = self.left.eval( context )

            if isinstance( events, Music ):
                for event in events:
                    yield event

    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        if isinstance( left_value, Music ):
            Value.expect( right_value, float, '* right side' )

            return Music( self.get_events( context, left_value, right_value ) )
        else:
            return left_value * right_value
    
class DivBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value / right_value
    
class AndLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )

        if not left_value: return False

        right_value = self.right.eval( context )

        return bool( right_value )

class OrLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )

        if left_value:
            return left_value

        right_value = self.right.eval( context )

        return right_value if right_value else False

ComparableValueKinds = Union[ int, float, str, bool ]

class ComparisonOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        Value.expect( left_value, ComparableValueKinds, f'{self.operator} left operator' )
        Value.expect( right_value, ComparableValueKinds, f'{self.operator} right operator' )
        
        return self.compare( left_value.value, right_value.value )

class GreaterEqualComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '>='

    def compare ( self, a, b ): return a >= b

class GreaterComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '>'

    def compare ( self, a, b ): return a > b

class EqualComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '=='

    def compare ( self, a, b ): return a == b

class NotEqualComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '!='

    def compare ( self, a, b ): return a != b

class LesserEqualComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '<='

    def compare ( self, a, b ): return a <= b

class LesserComparisonOperatorNode(ComparisonOperatorNode):
    operator : str = '<'

    def compare ( self, a, b ): return a < b
