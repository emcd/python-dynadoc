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


def _record_adjunct(
    entity: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
) -> None:
    if entity in ( __.types.UnionType, __.typx.Union ):
        adjuncts.traits.add( 'Union' )
        return
    if entity in ( __.typx.ClassVar, __.typx.Final ):
        label = entity.__name__
        if 'Union' in adjuncts.traits:
            emessage = f"Use of {label!r} within a union is invalid."
            context.notifier( 'admonition', emessage )
            return
        adjuncts.traits.add( label )


# TODO: Refactor (again).
#       * Focus on stripping Annotated plus filters.
#         By default, filters include ClassVar filter.
#         (Let Final remain as-is.)
#       * Replace typles with typx.Union.
#         Union returns single argument itself, so no special handling of
#         single arguments is needed.
#       * Pile all Annotated arguments into single bucket.
#         Formatters can look through this bucket for what they need.
#       * Inherit adjuncts data for single-argument typeforms.
#         Use severed adjuncts data for multiple-argument typeforms.
#         I.e., no special treatment of Callable, Generic, etc....
#       * Generic function to reconstitute all typeforms from their
#         filtered arguments. If argument is a sequence, then recurse into
#         sequence to filter and then reconstitute as same sequence.
#         (This handles the Callable case.) No special handling for Union
#         since it will naturally flatten any arguments which are unions.
#       * Ensure Ellipsis is left as-is in all cases.
# TODO? Cache object instead of visitees set. Has 'enter' method which
#       takes annotation (cache key) and reduced annotation (cache value).


def _reduce_annotation(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> _nomina.Typle:
    if annotation in visitees: return ( annotation, )
    # TODO? Eval strings. Should already be done by _access_annotations.
    visitees.add( annotation )
    origin = __.typx.get_origin( annotation )
    # bare types, typing.Any, typing.LiteralString, typing.Never,
    # typing.TypeVar have no origin; taken as-is
    # typing.Literal is considered fully reduced; taken as-is
    if origin in ( None, __.typx.Literal ): return ( annotation, )
    arguments = __.typx.get_args( annotation )
    if origin is __.typx.Annotated:
        _scan_adjuncts( arguments, context, adjuncts )
        return _reduce_annotation(
            annotation.__origin__, context, adjuncts, visitees )
    if issubclass( origin, __.cabc.Callable ):
        return _reduce_annotation_for_callable(
            origin, arguments, context, _interfaces.AdjunctsData( ), visitees )
    if isinstance( annotation, __.types.GenericAlias ):
        return _reduce_annotation_for_generic(
            origin, arguments, context, _interfaces.AdjunctsData( ), visitees )
    _record_adjunct( origin, context, adjuncts )
    return _reduce_annotation_arguments( # type guards, unions, etc...
        arguments, context, adjuncts, visitees )


def _reduce_annotation_arguments(
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> _nomina.Typle:
    return tuple( __.itert.chain.from_iterable( map(
        lambda a: _reduce_annotation( a, context, adjuncts, visitees ),
        arguments ) ) )


def _reduce_annotation_for_callable(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> _nomina.Typle:
    farguments, freturn = arguments
    farguments_r: list[ __.typx.Any ] = [ ]
    for argument in farguments:
        typle = _reduce_annotation(
            argument, context, _interfaces.AdjunctsData( ), visitees )
        farguments_r.append( __.typx.Union[ typle ] )
    freturn_r = __.typx.Union[ _reduce_annotation(
        freturn, context, _interfaces.AdjunctsData( ), visitees ) ]
    try: annotation = origin[ farguments_r, freturn_r ]
    except TypeError as exc:
        emessage = (
            f"Cannot reconstruct callable with reduced annotations "
            f"for arguments. Reason: {exc}" )
        context.notifier( 'error', emessage )
        return ( origin, )
    return ( annotation, )


def _reduce_annotation_for_generic(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    visitees: set[ __.typx.Any ],
) -> _nomina.Typle:
    arguments_r: list[ __.typx.Any ] = [ ]
    for argument in arguments:
        typle = _reduce_annotation(
            argument, context, _interfaces.AdjunctsData( ), visitees )
        arguments_r.append( __.typx.Union[ typle ] )
    try: annotation = origin[ arguments_r ]
    except TypeError as exc:
        emessage = (
            f"Cannot reconstruct generic {origin.__name__!r} "
            f"with reduced annotations for arguments. Reason: {exc}" )
        context.notifier( 'error', emessage )
        return ( origin, )
    return ( annotation, )


def _scan_adjuncts(
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
) -> None:
    if 'Union' in adjuncts.traits:
        emessage = (
            "Cannot disambiguate arguments to 'Annotated' within a union." )
        context.notifier( 'admonition', emessage )
        return
    for argument in arguments:
        if isinstance( argument, _interfaces.Doc ):
            adjuncts.documentation.append( argument )
        if isinstance( argument, _interfaces.Raises ):
            adjuncts.exceptions.append( argument )
