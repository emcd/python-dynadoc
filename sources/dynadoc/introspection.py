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
    possessor: _nomina.Decoratable,
    context: _interfaces.Context,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    if __.inspect.isclass( possessor ):
        return _introspect_class( possessor, context, cache )
    if __.inspect.isfunction( possessor ) and possessor.__name__ != '<lambda>':
        return _introspect_function( possessor, context, cache )
    # TODO? Other descriptors, like properties.
    return ( )


def is_attribute_visible(
    name: str, annotation: __.typx.Any, description: __.typx.Optional[ str ]
) -> bool:
    return bool( description ) or not name.startswith( '_' )


def _introspect_class(
    possessor: type,
    context: _interfaces.Context,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    # TODO: Support option to traverse MRO for inheritance.
    annotations = _access_annotations( possessor, context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    for name, annotation in annotations.items( ):
        adjuncts = _interfaces.AdjunctsData( )
        annotation_ = _reduce_annotation(
            annotation, context, adjuncts, cache )
        description = '\n\n'.join(
            extra.documentation for extra in adjuncts.extras
            if isinstance( extra, _interfaces.Doc ) )
        if not context.visibility_predicate(name, annotation_, description ):
            continue
        informations.append( _interfaces.AttributeInformation(
            name = name,
            annotation = annotation_,
            description = description,
            on_class = 'ClassVar' in adjuncts.traits ) )
    return tuple( informations )


def _introspect_function(
    possessor: __.cabc.Callable[ ..., __.typx.Any ],
    context: _interfaces.Context,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    try: signature = __.inspect.signature( possessor )
    except ValueError as exc:
        context.notifier(
            'error',
            f"Could not assess signature for {possessor.__qualname__!r}. "
            f"Reason: {exc}" )
        return ( )
    if signature.parameters:
        informations.extend( _introspect_function_valences(
            annotations, signature, context, cache ) )
    if 'return' in annotations:
        informations.extend( _introspect_function_return(
            annotations[ 'return' ], context, cache ) )
    return tuple( informations )


def _introspect_function_return(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    adjuncts = _interfaces.AdjunctsData( )
    annotation_ = _reduce_annotation( annotation, context, adjuncts, cache )
    description = '\n\n'.join(
        extra.documentation for extra in adjuncts.extras
        if isinstance( extra, _interfaces.Doc ) )
    informations.append(
        _interfaces.ReturnInformation(
            annotation = annotation_, description = description ) )
    informations.extend(
        _interfaces.ExceptionInformation(
            annotation = _classes_sequence_to_union( extra.classes ),
            description = extra.description )
        for extra in adjuncts.extras
        if isinstance( extra, _interfaces.Raises ) )
    return tuple( informations )


def _introspect_function_valences(
    annotations: __.cabc.Mapping[ str, __.typx.Any ],
    signature: __.inspect.Signature,
    context: _interfaces.Context,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ _interfaces.ArgumentInformation ]:
    informations: list[ _interfaces.ArgumentInformation ] = [ ]
    for name, param in signature.parameters.items( ):
        annotation = annotations.get( name, param.annotation )
        if annotation is param.empty: continue
        adjuncts = _interfaces.AdjunctsData( )
        annotation_ = _reduce_annotation(
            annotation, context, adjuncts, cache )
        description = '\n\n'.join(
            extra.documentation for extra in adjuncts.extras
            if isinstance( extra, _interfaces.Doc ) )
        informations.append( _interfaces.ArgumentInformation(
            name = name,
            annotation = annotation_,
            description = description,
            paramspec = param ) )
    return tuple( informations )


def _access_annotations(
    possessor: _nomina.Decoratable, context: _interfaces.Context
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    nomargs: _nomina.Variables = dict( eval_str = True )
    nomargs[ 'locals' ] = context.resolver_locals
    nomargs[ 'globals' ] = context.resolver_globals
    try:
        return __.types.MappingProxyType(
            __.inspect.get_annotations( possessor, **nomargs ) )
    except TypeError as exc:
        emessage = f"Cannot access annotations for {possessor!r}: {exc}"
        context.notifier( 'error', emessage )
        return __.dictproxy_empty


def _classes_sequence_to_union(
    annotation: type | __.cabc.Sequence[ type ]
) -> __.typx.Any:
    if not isinstance( annotation, __.cabc.Sequence ):
        return annotation
    return __.funct.reduce( __.operator.or_, annotation )


def _filter_reconstitute_annotation(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.typx.Any:
    adjuncts.traits.add( origin.__name__ )
    arguments_r: list[ __.typx.Any ] = [ ]
    match len( arguments ):
        case 1:
            arguments_r.append( _reduce_annotation(
                arguments[ 0 ], context, adjuncts, cache ) )
        case _:
            # upward propagation is ambiguous, so sever adjuncts data
            adjuncts_ = _interfaces.AdjunctsData( )
            adjuncts_.traits.add( origin.__name__ )
            arguments_r.extend( _reduce_annotation_arguments(
                origin, arguments, context, adjuncts_.copy( ), cache ) )
    # TODO: Apply filters from context, replacing origin as necessary.
    #       E.g., ClassVar -> Union
    #       (Union with one argument returns the argument.)
    try:
        if origin in ( __.types.UnionType, __.typx.Union ):
            # Unions cannot be reconstructed from sequences.
            # TODO: Python 3.11: Unpack into subscript.
            annotation = __.funct.reduce( __.operator.or_, arguments_r )
        else:
            annotation = origin[ tuple( arguments_r ) ]
    except TypeError as exc:
        emessage = (
            f"Cannot reconstruct {origin.__name__!r} "
            f"with reduced annotations for arguments. Reason: {exc}" )
        context.notifier( 'error', emessage )
        return origin
    # print( annotation )
    # print( adjuncts )
    # print( )
    return annotation


def _reduce_annotation(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.typx.Any:
    annotation_r = cache.access( annotation )
    # Avoid infinite recursion from reference cycles.
    if annotation_r is cache.incomplete:
        emessage = (
            f"Annotation with circular reference {annotation!r}; "
            "returning Any." )
        context.notifier( 'admonition', emessage )
        return cache.enter( annotation, __.typx.Any )
    # Short-circuit on cache hit.
    if annotation_r is not cache.absent: return annotation_r
    cache.enter( annotation ) # mark as incomplete
    return cache.enter(
        annotation,
        _reduce_annotation_core( annotation, context, adjuncts, cache ) )


def _reduce_annotation_arguments(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ __.typx.Any ]:
    if issubclass( origin, __.cabc.Callable ):
        return _reduce_annotation_for_callable(
            arguments, context, adjuncts.copy( ), cache )
    return tuple(
        _reduce_annotation( argument, context, adjuncts.copy( ), cache )
        for argument in arguments )


def _reduce_annotation_core(
    annotation: __.typx.Any,
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.typx.Any:
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
            annotation.__origin__, context, adjuncts, cache )
    return _filter_reconstitute_annotation(
        origin, arguments, context, adjuncts, cache )


def _reduce_annotation_for_callable(
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _interfaces.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> tuple[ list[ __.typx.Any ] | __.types.EllipsisType, __.typx.Any ]:
    farguments, freturn = arguments
    if farguments is Ellipsis:
        farguments_r = Ellipsis
    else:
        farguments_r = [
            _reduce_annotation( element, context, adjuncts.copy( ), cache )
            for element in farguments ]
    freturn_r = (
        _reduce_annotation( freturn, context, adjuncts.copy( ), cache ) )
    return ( farguments_r, freturn_r )
