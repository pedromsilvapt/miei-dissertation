import time
import hashlib
import tempfile
from pathlib import Path
from lark import Lark, UnexpectedInput
from typing import Optional
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

        self.internal_parser = self.create_parser( 
            read_cache = self.read_cache,
            write_cache = self.write_cache
        )

        self.specific_parsers = dict()

    def get_cache_path ( self, rule : Optional[str], content : str ) -> Path:
        cache_path = Path( tempfile.gettempdir() )

        if rule is not None:
            content = rule + "|" + content
        
        dig = hashlib.md5( content.encode() ).hexdigest()
            
        return cache_path / ( 'grammar.lark.pickle.' + dig + '.tmp' )

    def create_parser ( self, rule : str = None, read_cache : bool = True, write_cache : bool = True ):
        with open( Path( __file__ ).parent / "grammar.lark", "r" ) as f:
            grammar_content = f.read()

            cache_path = self.get_cache_path( rule, grammar_content ) if read_cache or write_cache else None

            parser = None

            if read_cache and cache_path.exists():
                with open( cache_path, "rb" ) as f:
                    parser = Lark.load( f )
            else:
                parser = Lark( grammar_content, start = rule or 'start', 
                    parser='lalr', debug=False, propagate_positions = True, 
                    maybe_placeholders = True )
            
                if write_cache:
                    with open( cache_path, "wb" ) as f:
                        parser.save( f )

            return parser

    def get_parser ( self, rule : str = None ):
        if rule is None or rule == "start":
            return self.internal_parser
        else:
            if rule not in self.specific_parsers:
                self.specific_parsers[ rule ] = self.create_parser( rule )
            
            return self.specific_parsers[ rule ]

    def parse ( self, expression, file : str = None, file_id : int = None, rule : str = None ) -> Node:
        try:
            parser = self.get_parser( rule )

            start_time = time.time()
            tree = MusiklaTransformer( file = file, file_id = file_id ).transform( parser.parse( expression ) )
            self.time_spent += time.time() - start_time

            return tree;
        except UnexpectedInput as err:
            raise ParserError( err, expression, file )

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