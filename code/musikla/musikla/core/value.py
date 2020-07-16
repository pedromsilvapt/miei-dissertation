from sys import base_exec_prefix
from typing import Any, Optional, Tuple
from typeguard import check_type
from .music import Music, MusicGen

class Value:
    @staticmethod
    def assignment ( value ):
        # TODO
        if isinstance( value, Music ):
            return value.shared()
        
        return value

    @staticmethod
    def forked ( value ):
        if isinstance( value, Music ):
            def _gen ( context ):
                for ev in value.expand( context ):
                    context.cursor = max( ev.end_timestamp, context.cursor )

                    yield ev

            return MusicGen( None, _gen )
        else:
            return value

    @staticmethod
    def expect ( value, typehint, name : str = "", soft : bool = False ) -> bool:
        if soft:
            try:
                check_type( name, value, typehint )

                return True
            except:
                return False
        else:
            check_type( name, value, typehint )
            
            return True

    @staticmethod
    def typeof ( value ):
        return type( value )

    @staticmethod
    def eval ( context, node ) -> Any:
        if node == None: 
            return None

        return node.eval( context )

class CallableValue:
    def __init__ ( self, fn ):
        self.fn = fn

    def __call__ ( self, context, args, kargs ):
        return self.fn( context, *args, **kargs )

    def raw ( self ):
        return self.fn
