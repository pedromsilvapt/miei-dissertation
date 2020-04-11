from musikla.parser.printer import CodePrinter
from ..node import Node
from .expression_node import ExpressionNode
from musikla.core import Value, Music
from typing import Optional, Tuple, Union

class BinaryOperatorNode( ExpressionNode ):
    def __init__ ( self, left : Node, right : Node, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.left : Node = left
        self.right : Node = right

    def eval ( self, context ):
        return None

class PlusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value + right_value

    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' + ' )

        self.right.to_source( printer )

class MinusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value - right_value
    
    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' - ' )

        self.right.to_source( printer )

class MultBinaryOperatorNode(BinaryOperatorNode):
    def get_events ( self, context, events : Music, count : int ):
        if count == 0: return

        for event in events.expand( context ):
            yield event

        for _ in range( 1, count ):
            events = self.left.eval( context )

            if isinstance( events, Music ):
                for event in events.expand( context ):
                    yield event

    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        if isinstance( left_value, Music ):
            Value.expect( right_value, float, '* right side' )

            return Music( self.get_events( context, left_value, right_value ) )
        else:
            return left_value * right_value
    
    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' * ' )

        self.right.to_source( printer )

class DivBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return left_value / right_value
    
    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' / ' )

        self.right.to_source( printer )

class AndLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )

        if not left_value: return False

        right_value = self.right.eval( context )

        return bool( right_value )

    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' and ' )

        self.right.to_source( printer )

class OrLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context ):
        left_value = self.left.eval( context )

        if left_value:
            return left_value

        right_value = self.right.eval( context )

        return right_value if right_value else False

    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' or ' )

        self.right.to_source( printer )

class ComparisonOperatorNode(BinaryOperatorNode):
    operator : Optional[str] = None

    def __init__ ( self, left : Node, right : Node, position : Tuple[int, int] = None ):
        super().__init__( left, right, position )

    def compare ( self, a, b ):
        pass

    def eval ( self, context, assignment : bool = False ):
        left_value = self.left.eval( context )
        right_value = self.right.eval( context )

        return self.compare( left_value, right_value )

    def to_source ( self, printer : CodePrinter ):
        self.left.to_source( printer )

        printer.add_token( ' ' + self.operator + ' ' )

        self.right.to_source( printer )

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

    def compare ( self, a, b ): 
        return a < b
