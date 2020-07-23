import sys
import time
from pathlib import Path
from lark import Lark, LarkError, UnexpectedInput
from typing import Any, List, Optional, Tuple, cast
from musikla.core.events import NoteEvent
from musikla.core.theory import NoteAccidental, Note, Chord
from .error_reporter import ErrorReporter
from .abstract_syntax_tree import Node
from .transformer import MusiklaTransformer


class Parser():
    def __init__ ( self, read_cache : bool = True, write_cache : bool = True ):
        self.debug : bool = False

        self.time_spent : float = 0
        self.lark_time_spent : float = 0
        self.read_cache : bool = read_cache
        self.write_cache : bool = write_cache

        cache_path = Path( __file__ ).parent / "grammar.lark.pickle"
        
        if not self.read_cache or not cache_path.exists():
            with open( Path( __file__ ).parent / "grammar.lark", "r" ) as f:
                self.internal_parser = Lark( f.read(), parser='lalr', debug=False, propagate_positions = True, maybe_placeholders = True )

            if self.write_cache:
                with open( cache_path, "wb" ) as f:
                    self.internal_parser.save(f)
        else:
            with open( cache_path, "rb" ) as f:
                self.internal_parser = Lark.load(f)

        self.specific_parsers = dict()


    def create_parser ( self, rule : str, memoization : bool = True, debug : bool = False ):
        with open( Path( __file__ ).parent / "grammar.lark", "r" ) as f:
            self.internal_parser = Lark( f.read(), start = rule, parser='lalr', debug=False, propagate_positions = True, maybe_placeholders = True )

    def get_parser ( self, rule : str = None ):
        if rule is None or rule == "main":
            return self.internal_parser
        else:
            if rule not in self.specific_parsers:
                self.specific_parsers[ rule ] = self.create_parser( rule )
                print( rule )
            
            return self.specific_parsers[ rule ]

    def parse ( self, expression, file : str = None, file_id : int = None, rule : str = None ) -> Node:
        try:
            start_time = time.time()
            tree = MusiklaTransformer( file = file, file_id = file_id ).transform( self.internal_parser.parse( expression ) )
            self.time_spent += time.time() - start_time

            return tree;
        except UnexpectedInput as err:
            raise ParserError( err, expression, file )
            raise err from None


    def parse_file ( self, file ) -> Node:
        with open( file, 'r', encoding="utf-8" ) as f:
            return self.parse( f.read(), file = file )

class ParserError(Exception):
    def __init__ ( self, err : UnexpectedInput, contents : str, file : str = None ):
        super().__init__()
        
        self.reporter = ErrorReporter( "ParseError", str( err ).split('Expected')[ 0 ], contents, ( err.pos_in_stream, err.pos_in_stream + 1 ), file )

    def __repr__ ( self ):
        return str( self.reporter )

    def __str__ ( self ):
        return str( self.reporter )