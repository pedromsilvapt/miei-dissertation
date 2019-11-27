from .value import Value, CallableValue
from .context import Context
from parser.abstract_syntax_tree.node import Node

from typing import get_type_hints, Union, Optional, _GenericAlias
from inspect import signature, Signature, Parameter
from typeguard import check_type

def is_type_of ( typehint, value ) -> bool:
    if issubclass( typehint, _GenericAlias ):
        origin = typehint.__origin__

        if origin == Union or origin == Optional:
            return any( is_type_of( var, value ) for var in typehint.__args__ )
        else:
            return False
    else:
        return value == typehint

class CallablePythonValue(CallableValue):
    def __init__ ( self, value ):
        self.signature : Signature = signature( value )
        self.callable = value

        super().__init__( self.wrapper )

    def eval_argument ( self, context, parameter : Parameter, node : Node, arg_name : str ):
        if is_type_of( parameter.annotation, Node ):
            return node

        value = Value.eval( context.fork(), node )

        if parameter.annotation != Parameter.empty:
            check_type( arg_name, value, parameter.annotation )
        
        return value

    def wrapper ( self, context, *args, **kargs ):
        # Value.eval( context, node ).value for node in args
        args_values = list()

        # ( name, Value.eval( context, node ).value ) for name, node in args
        kargs_values = dict()

        pass_context : bool = False
        i = 0

        for arg_name in self.signature.parameters:
            parameter = self.signature.parameters[ arg_name ]

            if i == 0 and not pass_context and is_type_of( parameter.annotation, Context ):
                pass_context = True

                args_values.append( context )

                continue

            # Let's treat this as positional arguments
            if i < len( args ):
                args_values.append( self.eval_argument( context, parameter, args[ i ], arg_name ) )
            # Treat this as keywork arguments
            else:
                if arg_name in kargs:
                    kargs_values[ arg_name ] = self.eval_argument( context, parameter, kargs[ arg_name ], arg_name )

            i = i + 1

        return self.callable( *args_values, **kargs_values )
