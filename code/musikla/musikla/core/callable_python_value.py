from .value import Value, CallableValue
from .context import Context
from .symbols_scope import Ref
from musikla.parser.abstract_syntax_tree.node import Node
from musikla.parser.abstract_syntax_tree.expressions.string_literal_node import StringLiteralNode
from musikla.parser.abstract_syntax_tree.expressions.variable_expression_node import VariableExpressionNode

from typing import Union, Optional, _GenericAlias, Dict
from inspect import signature, Signature, Parameter
from typeguard import check_type

def is_type_of ( typehint, value ) -> bool:
    if value == typehint:
        return True
    elif isinstance( typehint, _GenericAlias ):
        origin = typehint.__origin__

        if origin == Union or origin == Optional:
            return any( is_type_of( var, value ) for var in typehint.__args__ )
        else:
            return False
    else:
        return False

class CallablePythonValue(CallableValue):
    @staticmethod
    def call ( fn, context, args = [], kargs = {} ):
        if isinstance( fn, CallableValue ):
            return fn( context, args, kargs )
        else:
            return CallablePythonValue( fn )( context, args, kargs )

    @staticmethod
    def raw_call ( callable, context ):
        def closure ( *args, **kargs ):
            nonlocal context

            literal_args = [ StringLiteralNode( value ) for value in args ]
            literal_kargs = dict( ( key, StringLiteralNode( value ) ) for key, value in kargs.items() )

            return callable( context, literal_args, literal_kargs )

        return closure

    def __init__ ( self, value ):
        try:
            self.signature : Signature = signature( value )
        except ValueError:
            self.signature : Signature = None

        self.callable = value

        super().__init__( self.wrapper )

    def raw ( self ):
        return self.callable

    def eval_argument ( self, context : Context, parameter : Parameter, node : Node, arg_name : str ):
        if is_type_of( parameter.annotation, Node ):
            return node

        if is_type_of( parameter.annotation, Ref ):
            check_type( arg_name, node, VariableExpressionNode )

            pointer = context.symbols.pointer( node.name )

            return Ref( pointer )

        value = Value.eval( context.fork(), node )

        if parameter.annotation != Parameter.empty:
            check_type( arg_name, value, parameter.annotation )
        
        if isinstance( value, CallableValue ):
            return CallablePythonValue.raw_call( value, context )

        return value

    def eval_var_keyword ( self, context : Context, parameter : Parameter, nodes : Dict[ str, Node ] ):
        return dict( ( key, self.eval_argument( context, parameter, value, key ) ) for key, value in nodes.items() )

    def wrapper ( self, context, *args, **kargs ):
        args_values = list()

        kargs_values = dict()

        if self.signature != None:
            pass_context : bool = False

            i = 0

            for arg_name in self.signature.parameters:
                parameter = self.signature.parameters[ arg_name ]

                if i == 0 and not pass_context and is_type_of( parameter.annotation, Context ):
                    pass_context = True

                    args_values.append( context )

                    continue

                # Let's treat this as positional arguments
                if parameter.kind == Parameter.VAR_POSITIONAL:
                    while i < len( args ):
                        args_values.append( self.eval_argument( context, parameter, args[ i ], arg_name ) )

                        i = i + 1
                elif i < len( args ):
                    args_values.append( self.eval_argument( context, parameter, args[ i ], arg_name ) )

                    i = i + 1
                # Treat this as keywork arguments~
                elif parameter.kind == Parameter.VAR_KEYWORD:
                    kargs_values.update( self.eval_var_keyword( context, parameter, kargs ) )
                else:
                    if arg_name in kargs:
                        kargs_values[ arg_name ] = self.eval_argument( context, parameter, kargs[ arg_name ], arg_name )
        else:
            args_values = [ Value.eval( context.fork(), node ) for node in args ]

            kargs_values = dict( [ ( key, Value.eval( context.fork(), node ) ) for key, node in kargs ] )

        return self.callable( *args_values, **kargs_values )
