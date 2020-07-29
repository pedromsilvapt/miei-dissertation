import unittest
from musikla.parser.printer import CodePrinter
from musikla.parser.parser import Parser

parser = Parser()

class ParserTestCase(unittest.TestCase):
    def setUp ( self ):
        self.parser = parser
        self.printer = CodePrinter()

    def assertParse ( self, source, expected = None ):
        if expected is None:
            expected = source

        ast = self.parser.parse( source )

        source_printed = self.printer.print( ast )

        self.assertEqual( source_printed, expected )

    def test_number ( self ):
        self.assertParse( "1" )
        self.assertParse( "1.2" )
        self.assertParse( "+1", "1" )
        self.assertParse( "-1" )

    def test_string ( self ):
        self.assertParse( "'ola'" )
        self.assertParse( '"ola"', "'ola'" )

    def test_notes ( self ):
        self.assertParse( "a" )
        self.assertParse( "A" )
        self.assertParse( "C," )
        self.assertParse( "C,/2", "C,1/2" )
        self.assertParse( "C,2/2", "C," )
        self.assertParse( "C,3/2" )
        self.assertParse( "C,3" )
        self.assertParse( "c'''" )
        self.assertParse( "__c'''" )
        self.assertParse( "_c'''" )
        self.assertParse( "^^c'''" )
        self.assertParse( "^c'''" )

    def test_chords ( self ):
        self.assertParse( "[CFG,]" )
        
        # Shortcuts
        self.assertParse( "[Fm3]" )
        self.assertParse( "[FM3]" )            
        self.assertParse( "[Fm7]" )
        self.assertParse( "[FM7]" )
        self.assertParse( "[Fdom7]" )
        self.assertParse( "[F7]" )
        self.assertParse( "[Fm7b5]" )
        self.assertParse( "[Fdim7]" )
        self.assertParse( "[FmM7]" )
        self.assertParse( "[F5]" )
        self.assertParse( "[FM]" )
        self.assertParse( "[Fm]" )
        self.assertParse( "[Faug]" )
        self.assertParse( "[Fdim]" )
        self.assertParse( "[F]" )

        self.assertParse( "[F+]" )
        self.assertParse( "[F+]1/2" )
        self.assertParse( "[F__G^A]4/3" )

    def test_attribution ( self ):
        self.assertParse( "$a = 1" )
        self.assertParse( "$a::m = 1" )
        self.assertParse( "$a::m::[1] = 1" )
        self.assertParse( "$a::m::n::[1] = 1" )
        self.assertParse( "($a::m::n)::[1] = 1" )

    def test_if_statement ( self ):
        self.assertParse( "if (1) {2} else {3}" )
        self.assertParse( "if (1) 2 else 3" )
        self.assertParse( "if 1 {2} else 3" )
        self.assertParse( "if 1 then 2 else 3" )
        self.assertParse( "if 1 then 2 else if 3 then 4 else 5" )

    def test_while_statement ( self ):
        self.assertParse( "while (1) {2}" )
        self.assertParse( "while (1) 2" )
        self.assertParse( "while 1 {2}" )
        self.assertParse( "while 1 then 2" )
        
