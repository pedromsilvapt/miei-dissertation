import unittest
from musikla.core import Context, Value
from musikla.parser.parser import Parser
from musikla.libraries.std import StandardLibrary

parser = Parser()

class EvalTestCase(unittest.TestCase):
    def setUp ( self ):
        self.parser = parser
        self.context = Context.create()
        self.context.link( StandardLibrary( None ) )

    def assertEval ( self, source, value ):
        ast = self.parser.parse( source )

        result = Value.eval( self.context, ast )

        self.assertEqual( result, value )

    def test_number ( self ):
        self.assertEval( "1", 1 )
        self.assertEval( "1.2", 1.2 )
        self.assertEval( "+1", 1 )
        self.assertEval( "-1", -1 )

    def test_string ( self ):
        self.assertEval( "'ola'", "ola" )
        self.assertEval( '"ola"', 'ola' )

    def test_if ( self ):
        self.assertEval( "if true then 1 else 2", 1 )
        self.assertEval( "if false then 1 else 2", 2 )
        self.assertEval( "if true then 1 else if true then 2 else 3", 1 )
        self.assertEval( "if false then 1 else if true then 2 else 3", 2 )
        self.assertEval( "if false then 1 else if false then 2 else 3", 3 )
    
    def test_operators ( self ):
        self.assertEval( "1 + 2", 3 )
        self.assertEval( "1 - 2", -1 )
        self.assertEval( "3 * 2", 6 )
        self.assertEval( "6 / 2", 3 )
        self.assertEval( "1 / 2", 0.5 )
        # Operator Precedence
        self.assertEval( "1 + 2 * 2", 5 )
        self.assertEval( "1 + 2 * 2 / 2", 3 )
        self.assertEval( "1 + 2 * 2 / 2 + 1", 4 )
        self.assertEval( "2 ** 3", 2 ** 3 )

        # Comparison Operators
        self.assertEval( "1 > 0", True )
        self.assertEval( "1 >= 0", True )
        self.assertEval( "1 < 0", False )
        self.assertEval( "1 <= 0", False )
        self.assertEval( "1 != 0", True )
        self.assertEval( "1 == 0", False )
        self.assertEval( "2 != 2", False )
        self.assertEval( "2 == 2", True )

        # Logical Operators
        self.assertEval( "true or false", True )
        self.assertEval( "false or false", False )
        self.assertEval( "true and false", False )
        self.assertEval( "true and true", True )
        self.assertEval( "not true or true", True )
        self.assertEval( "not true or false", False )

        self.assertEval( "true is $bool", True )
        self.assertEval( "true isnot $bool", False )
        self.assertEval( "none isnot none", False )
        self.assertEval( "0 is none", False )
        self.assertEval( "0 isnot none", True )

        self.assertEval( "0 in @[ 1, 2, 3 ]", False )
        self.assertEval( "0 notin @[ 1, 2, 3 ]", True )
        self.assertEval( "1 in @[ 1, 2, 3 ]", True )
        self.assertEval( "1 notin @[ 1, 2, 3 ]", False )

    def test_functions ( self ):
        self.assertEval( "fun fn ($a, $b = 2) => $a * $b; none", None )
        self.assertEval( "fn(4)", 8 )
        self.assertEval( "fn(4, 3)", 12 )
        self.assertEval( "fn(4, b = 3)", 12 )
        self.assertEval( "fn(a = 4, b = 3)", 12 )

        # Ref Parameters
        self.assertEval( "fun fn ( ref $a, $b ) { $a = $b }; $c = 2", None )
        self.assertEval( "fn($c; 4); $c", 4 )

    def test_assignment ( self ):
        self.assertEval( "$a = 1234; $a", 1234 )
        self.assertEval( "$a = 1234; { $a = 12 }; $a", 12 )
        self.assertEval( "$a = 10; while $a > 0 { $a -= 1 }; $a", 0 )
        self.assertEval( "$a = 0; while $a < 10 { $a += 1 }; $a", 10 )