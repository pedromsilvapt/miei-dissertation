from ..node import Node
from .expression_node import ExpressionNode
from core import Value, VALUE_KIND_NUMBER, VALUE_KIND_STRING, VALUE_KIND_BOOL, VALUE_KIND_MUSIC

class BinaryOperatorNode( ExpressionNode ):
    def __init__ ( self, left : Node, right : Node, position : (int, int) = None ):
        super().__init__( position )

        self.left : Node = left
        self.right : Node = right

    def eval ( self, context, assignment : bool = False ):
        return self.value

class PlusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value.kind == VALUE_KIND_STRING or right_value.kind == VALUE_KIND_STRING:
            return Value( VALUE_KIND_STRING, str( left_value.value ) + str( right_value.value ) )
        elif left_value.kind == VALUE_KIND_NUMBER and left_value.kind == VALUE_KIND_NUMBER:
            return Value( VALUE_KIND_NUMBER, left_value.value + right_value.value )
        else:
            raise BaseException( "Expected strings or numbers for plus operator" )

class MinusBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value.kind == VALUE_KIND_NUMBER and left_value.kind == VALUE_KIND_NUMBER:
            return Value( VALUE_KIND_NUMBER, left_value.value - right_value.value )
        else:
            raise BaseException( "Expected numbers for minus operator" )

class MultBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value.kind == VALUE_KIND_NUMBER and left_value.kind == VALUE_KIND_NUMBER:
            return Value( VALUE_KIND_NUMBER, left_value.value - right_value.value )
        else:
            raise BaseException( "Expected numbers for minus operator" )
    
class MultBinaryOperatorNode(BinaryOperatorNode):
    def get_events ( self, context, events, count ):
        for event in events:
            yield event

        for i in range( 1, count ):
            events = self.left.eval( context )

            if events != None and events.is_music:
                for event in events:
                    yield event

    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value.kind == VALUE_KIND_MUSIC:
            if right_value.kind != VALUE_KIND_NUMBER:
                raise BaseException( "'*' not supported between instances of 'Music' and %s" % right_value.kind )

            return Value( VALUE_KIND_MUSIC, self.get_events( context, left_value, right_value.value ) )
        elif left_value.kind == VALUE_KIND_NUMBER and right_value.kind == VALUE_KIND_NUMBER:
            return Value( VALUE_KIND_NUMBER, left_value.value * right_value.value )
        else:
            raise BaseException( "Expected numbers for multiplication operator" )
    
class DivBinaryOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value.kind == VALUE_KIND_NUMBER and left_value.kind == VALUE_KIND_NUMBER:
            return Value( VALUE_KIND_NUMBER, left_value.value / right_value.value )
        else:
            raise BaseException( "Expected numbers for division operator" )
    
class AndLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )

        if left_value == None or not left_value.value:
            return Value( VALUE_KIND_BOOL, False )

        right_value : Value = self.right.eval( context )

        return Value( VALUE_KIND_BOOL, right_value != None and right_value.value )

class OrLogicOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )

        if left_value != None and left_value.value:
            return left_value

        right_value : Value = self.right.eval( context )

        return right_value if right_value != None and right_value.value else Value.create( False )

ComparableValueKinds = [ VALUE_KIND_NUMBER, VALUE_KIND_STRING, VALUE_KIND_BOOL ]

class ComparisonOperatorNode(BinaryOperatorNode):
    def eval ( self, context, assignment : bool = False ):
        left_value : Value = self.left.eval( context )
        right_value : Value = self.right.eval( context )

        if left_value == None or right_value == None:
            raise BaseException( "'%s' not supported between instances of 'None'" % self.operator )

        if left_value.kind not in ComparableValueKinds:
            raise BaseException( "'%s' not supported between instances of '%s'" % ( self.operator, left_value.kind ) )

        if right_value.kind not in ComparableValueKinds:
            raise BaseException( "'%s' not supported between instances of '%s'" % ( self.operator, right_value.kind ) )
        
        return Value( VALUE_KIND_BOOL, self.compare( left_value.value, right_value.value ) )

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
