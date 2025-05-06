# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Introspection of argument, attribute, and return annotations. '''


from __future__ import annotations

from . import __
from . import interfaces as _interfaces
from . import nomina as _nomina


def introspect(
    possessor: _nomina.Decoratable, context: _interfaces.Context
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    if __.inspect.isclass( possessor ):
        return _introspect_class( possessor, context )
    if __.inspect.isfunction( possessor ) and possessor.__name__ != '<lambda>':
        return _introspect_function( possessor, context )
    # TODO? Other descriptors, like properties.
    return ( )


def _introspect_class(
    possessor: _nomina.Decoratable, context: _interfaces.Context
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    for annotation in annotations:
        # TODO: Introspect attribute annotation.
        pass
    return tuple( informations )


def _introspect_function(
    possessor: _nomina.Decoratable, context: _interfaces.Context
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    # TODO: Implement.
    return tuple( informations )


def _access_annotations(
    possessor: _nomina.Decoratable, context: _interfaces.Context
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    nomargs: _nomina.Variables = dict( eval_str = True )
    if context:
        nomargs[ 'locals' ] = context.localvars
        nomargs[ 'globals' ] = context.globalvars
    try:
        return __.types.MappingProxyType(
            __.inspect.get_annotations( possessor, **nomargs ) )
    except TypeError as exc:
        emessage = f"Cannot access annotations for {possessor!r}: {exc}"
        context.notifier( 'error', emessage )
        return __.dictproxy_empty


# TODO? Cache object instead of visitees set. Has 'enter' method which
#       takes annotation (cache key) and reduced annotation (cache value).


def _filter_reconstitute_annotation(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> __.typx.Any:
    adjuncts.traits.add( origin.__name__ )
    arguments_r: list[ __.typx.Any ] = [ ]
    match len( arguments ):
        case 1:
            arguments_r.append( _reduce_annotation_argument(
                arguments[ 0 ], context, adjuncts, visitees ) )
        case _:
            # upward propagation is ambiguous, so sever adjuncts data
            adjuncts_ = _interfaces.AdjunctsData( )
            adjuncts_.traits.add( origin.__name__ )
            arguments_r.extend(
                _reduce_annotation_argument(
                    argument, context, adjuncts_.copy( ), visitees )
                for argument in arguments )
    # TODO: Apply filters from context, replacing origin as necessary.
    #       E.g., ClassVar -> Union
    #       (Union with one argument returns the argument.)
    try: annotation = origin[ tuple( arguments_r ) ]
    except TypeError as exc:
        emessage = (
            f"Cannot reconstruct {origin.__name__!r} "
            f"with reduced annotations for arguments. Reason: {exc}" )
        context.notifier( 'error', emessage )
        return origin
    return annotation


def _reduce_annotation(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> __.typx.Any:
    # if annotation in visitees: return ( annotation, )
    # TODO? Eval strings. Should already be done by _access_annotations.
    # visitees.add( annotation )
    origin = __.typx.get_origin( annotation )
    # bare types, Ellipsis, typing.Any, typing.LiteralString, typing.Never,
    # typing.TypeVar have no origin; taken as-is
    # typing.Literal is considered fully reduced; taken as-is
    if origin in ( None, __.typx.Literal ): return annotation
    arguments = __.typx.get_args( annotation )
    if not arguments: return annotation
    if origin is __.typx.Annotated:
        adjuncts.extras.extend( arguments[ 1 : ] )
        return _reduce_annotation(
            annotation.__origin__, context, adjuncts, visitees )
    return _filter_reconstitute_annotation(
        origin, arguments, context, adjuncts, visitees )


def _reduce_annotation_argument(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> __.typx.Any:
    if isinstance( annotation, __.cabc.Sequence ): # Callable, etc...
        elements: list[ __.typx.Any ] = [
            _reduce_annotation( element, context, adjuncts, visitees )
            for element in annotation ] # pyright: ignore[reportUnknownVariableType]
        return elements
    return _reduce_annotation( annotation, context, adjuncts, visitees )
