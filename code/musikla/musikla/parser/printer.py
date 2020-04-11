from typing import List, Optional

class CodePrinter:
    def __init__ ( self, ident : int = 4 ):
        self.ident : int = ident
        self.tokens : List[str] = []
        self.stack : List['CodeBlock'] = [ CodeBlock( 0, None, None, 'always' ) ]

    def block ( self, opening : Optional[str] = '{', closing : Optional[str] = '}', multiline : str = 'auto' ) -> 'CodeBlockContext':
        return CodeBlockContext( self, opening, closing, multiline )

    def begin_block ( self, opening : Optional[str] = '{', closing : Optional[str] = '}', multiline : str = 'auto' ):
        if opening is not None:
            self.add_token( opening )

        self.stack.append( CodeBlock( self.ident * len( self.stack ), opening, closing, multiline ) )

    def begin_line ( self ):
        self.stack[ -1 ].add_line()

    def add_token ( self, token : str ):
        self.stack[ -1 ].add_token( token )

    def end_block ( self ):
        block = self.stack.pop()

        self.stack[ -1 ].add_block( block )

    def print ( self, node ) -> str:
        node.to_source( self )

        return ''.join( self.stack[ -1 ].tokens )

class CodeBlockContext:
    def __init__ ( self, printer : CodePrinter, opening : Optional[str] = '{', closing : Optional[str] = '}', multiline_strat : str = 'auto' ):
        self.printer : CodePrinter = printer
        self.opening : Optional[str] = opening
        self.closing : Optional[str] = closing
        self.multiline_strat : str = multiline_strat
    
    def __enter__ ( self ):
        self.printer.begin_block( self.opening, self.closing, self.multiline_strat )

        return self
    
    def __exit__ ( self, exc_type, exc_val, exc_tb ):
        self.printer.end_block()

class CodeBlock:
    def __init__ ( self, ident : int, opening : Optional[str] = '{', closing : Optional[str] = '}', multiline_strat : str = 'auto' ):
        self.ident : int = ident
        self.opening : Optional[str] = opening
        self.closing : Optional[str] = closing
        self.multiline_strat : str = multiline_strat
        self.tokens : List[str] = []
        self.line_number : int = 0

    @property
    def multiline ( self ) -> bool:
        return ( self.line_number > 1 and self.multiline_strat != 'never' )\
            or ( self.multiline_strat == 'always' and self.line_number == 1 )

    def get_new_line ( self ) -> str:
        linebreak = ( '\n' if self.line_number > 0 or self.opening is not None else '' )

        return linebreak + ( ' ' * self.ident )

    def add_line ( self ):
        if self.line_number == 1 and self.multiline_strat == 'auto':
            self.tokens.insert( 0, self.get_new_line() )

        if ( self.line_number > 0 and self.multiline_strat != 'never' ) or self.multiline_strat == 'always':
            self.tokens.append( self.get_new_line() )
        
        self.line_number += 1

    def add_token ( self, token : str ):
        if self.line_number == 0:
            self.add_line()

        self.tokens.append( token )

    def add_block ( self, block : 'CodeBlock' ):
        self.tokens.extend( block.tokens )

        if block.multiline:
            self.add_line()

        if block.closing is not None:
            self.add_token( block.closing )