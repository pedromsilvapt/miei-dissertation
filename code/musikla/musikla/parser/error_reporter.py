from typing import List, Optional, Tuple
from colorama import Fore, Back, Style

class ErrorReporter:
    def __init__ ( self, error_phase : str, error_message : str, contents : str, position : Tuple[int, int], file : str = None ):
        self.error_phase : str = error_phase
        self.error_message : str = error_message
        self.contents : str = contents
        self.position : Tuple[int, int] = position
        self.file : Optional[str] = file

    def _is_newline ( self, char : str ) -> bool:
        return char == '\n'

    # Returns the (start_line, error_line, line_offsets)
    def _get_line_offsets ( self, adjacent_lines : int = 3 ) -> Tuple[int, int, List[int]]:
        error_line : int = -1

        start_line : int = 0

        line_offsets : List[int] = [ 0 ]

        line_offsets_count : int = 1

        line_offsets_index : int = 1

        max_lines : int = adjacent_lines * 2 + 2

        remaining_lines : int = adjacent_lines + 1

        for i in range( len( self.contents ) ):
            if i == self.position[ 0 ]:
                error_line = start_line + line_offsets_count - 1
            
            if self._is_newline( self.contents[ i ] ):
                if line_offsets_count < max_lines:
                    line_offsets.append( i )

                    line_offsets_count += 1
                else:
                    if error_line >= 0 and start_line == error_line:
                        break

                    line_offsets[ line_offsets_index ] = i

                    start_line += 1
                
                line_offsets_index = ( line_offsets_index + 1 ) % max_lines
                
                if i >= self.position[ 1 ]:
                    remaining_lines -= 1
                
                if remaining_lines == 0:
                    break
        
        if error_line < 0:
            error_line = start_line + line_offsets_count - 1

        return ( start_line, error_line, line_offsets[ line_offsets_index: ] + line_offsets[ :line_offsets_index ] )

    def _number_digits ( self, n ):
        return len( str( int( n ) ) )

    def __str__ ( self ):
        lines : List[str] = []

        def println ( ln = '' ):
            lines.append( ln )

        start_line, error_line, line_offsets = self._get_line_offsets()

        max_digits = self._number_digits( start_line + len( line_offsets ) + 1 )

        println()

        line = str( error_line + 1 )
        col = str( self.position[ 0 ] - line_offsets[ error_line - start_line ] + 1 )
        println( Back.RED + " " + self.error_phase + " " + Style.RESET_ALL + " in " + Fore.CYAN + ( self.file or "<in memory>" ) + Style.RESET_ALL + ":" + line + ":" + col  )
        
        for i in range( len( line_offsets ) - 1 ):
            start = line_offsets[ i ] + 1
            end = line_offsets[ i + 1 ] + 1

            number = start_line + i + 1

            number_str = format( number, '0' + str(max_digits) ) + " |"

            if start_line + i == error_line:
                number_str = Fore.RED + number_str + Style.RESET_ALL

            if self.position[ 0 ] >= start and self.position[ 1 ] <= end:
                line_str = self.contents[ start:self.position[ 0 ] ] \
                         + Back.RED + self.contents[ self.position[ 0 ]:self.position[ 1 ] ] + Style.RESET_ALL \
                         + self.contents[ self.position[ 1 ]:end - 1 ]
            elif self.position[ 0 ] >= start and self.position[ 0 ] < end and self.position[ 1 ] >= end:
                line_str = self.contents[ start:self.position[ 0 ] ] \
                         + Back.RED + self.contents[ self.position[ 0 ]:end - 1 ] + Style.RESET_ALL
            elif self.position[ 0 ] < start and self.position[ 1 ] > start and self.position[ 1 ] <= end:
                line_str = Back.RED + self.contents[ start:self.position[ 1 ] ] + Style.RESET_ALL \
                         + self.contents[ self.position[ 1 ]:end - 1 ]
            elif self.position[ 0 ] < start and self.position[ 1 ] > end:
                line_str = Back.RED + self.contents[ start:end - 1 ] + Style.RESET_ALL
            else:
                line_str = self.contents[ start:end ]

            println( f" {number_str}  {line_str}".strip() )
        
        println()
        println( Fore.RED + "Message " + Style.RESET_ALL + self.error_message )
        println()

        return '\n'.join( lines )
    
    def print ( self ):
        print( str( self ) )
