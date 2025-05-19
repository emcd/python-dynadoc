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


from . import __
from . import context as _context
from . import interfaces as _interfaces
from . import nomina as _nomina


_default_default = _interfaces.Default( )
_default_suppress = _interfaces.Default(
    mode = _interfaces.ValuationModes.Suppress )


def introspect(
    possessor: _nomina.Documentable, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    if __.inspect.isclass( possessor ):
        return _introspect_class(
            possessor, context, introspection, cache, table )
    if __.inspect.isfunction( possessor ) and possessor.__name__ != '<lambda>':
        return _introspect_function(
            possessor, context, cache, table )
    if __.inspect.ismodule( possessor ):
        return _introspect_module(
            possessor, context, introspection, cache, table )
    return ( )


def introspect_special_classes( # noqa: PLR0913
    objct: type,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    annotations: _nomina.Annotations,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.typx.Optional[ _interfaces.Informations ]:
    ''' Introspects special classes in Python standard library.

        E.g., enum members are collected as class variables.
    '''
    informations: list[ _interfaces.InformationBase ] = [ ]
    if isinstance( objct, __.enum.EnumMeta ):
        for name, member in objct.__members__.items( ): # noqa: PERF102
            informations.append( _interfaces.AttributeInformation(
                name = name,
                annotation = objct,
                description = None,
                association = _interfaces.AttributeAssociations.Class,
                default = _default_suppress ) )
        return informations
    return None


def is_attribute_visible(
    name: str, annotation: __.typx.Any, description: __.typx.Optional[ str ]
) -> bool:
    return (
        bool( description )
        # or (    name.startswith( '__' )
        #     and name.endswith( '__' )
        #     and len( name ) > 4 )
        or not name.startswith( '_' ) )


def reduce_annotation(
    annotation: __.typx.Any,
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.typx.Any:
    annotation_r = cache.access( annotation )
    # Avoid infinite recursion from reference cycles.
    if annotation_r is _interfaces.incomplete:
        emessage = (
            f"Annotation with circular reference {annotation!r}; "
            "returning Any." )
        context.notifier( 'admonition', emessage )
        return cache.enter( annotation, __.typx.Any )
    # Short-circuit on cache hit.
    if annotation_r is not _interfaces.absent: return annotation_r
    cache.enter( annotation ) # mark as incomplete
    return cache.enter(
        annotation,
        _reduce_annotation_core( annotation, context, adjuncts, cache ) )


def _access_annotations(
    possessor: _nomina.Documentable, context: _context.Context
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    nomargs: _nomina.Variables = dict( eval_str = True )
    nomargs[ 'globals' ] = context.resolver_globals
    nomargs[ 'locals' ] = context.resolver_locals
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


def _compile_description(
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    table: _nomina.FragmentsTable,
) -> str:
    fragments: list[ str ] = [ ]
    for extra in adjuncts.extras:
        if isinstance( extra, _interfaces.Doc ):
            fragments.append( extra.documentation )
        elif isinstance( extra, _interfaces.Findex ):
            name = extra.name
            if name not in table:
                emessage = f"Fragment '{name}' not in provided table."
                context.notifier( 'error', emessage )
            else: fragments.append( table[ name ] )
    return '\n\n'.join(
        context.fragment_rectifier( fragment ) for fragment in fragments )


def _determine_default_valuator(
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
) -> _interfaces.Default:
    return next(
        (   extra for extra in adjuncts.extras
            if isinstance( extra, _interfaces.Default ) ),
        _default_default )


def _filter_reconstitute_annotation(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.typx.Any:
    adjuncts.traits.add( origin.__name__ )
    arguments_r: list[ __.typx.Any ] = [ ]
    match len( arguments ):
        case 1:
            arguments_r.append( reduce_annotation(
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
            match len( arguments_r ):
                case 1: annotation = origin[ arguments_r[ 0 ] ]
                case _: annotation = origin[ tuple( arguments_r ) ]
    except TypeError as exc:
        emessage = (
            f"Cannot reconstruct {origin.__name__!r} "
            f"with reduced annotations for arguments. Reason: {exc}" )
        context.notifier( 'error', emessage )
        return origin
    return annotation


def _introspect_class(
    possessor: type,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations_: dict[ str, __.typx.Any ] = { }
    if introspection.class_control.inheritance:
        # Descendant annotations override ancestor annotations.
        for class_ in reversed( possessor.__mro__ ):
            annotations_b = _access_annotations( class_, context )
            annotations_.update( annotations_b )
        annotations = annotations_
    else: annotations = _access_annotations( possessor, context )
    informations: list[ _interfaces.InformationBase ] = [ ]
    for introspector in introspection.class_control.introspectors:
        informations_ = introspector(
            possessor,
            context = context, introspection = introspection,
            annotations = annotations, cache = cache, table = table )
        if informations_ is not None:
            informations.extend( informations_ )
            break
    else:
        informations.extend( _introspect_class_annotations(
            possessor, context, annotations, cache, table ) )
        if introspection.class_control.scan_attributes:
            informations.extend( _introspect_class_attributes(
                possessor, context, annotations ) )
    return tuple( informations )


def _introspect_class_annotations(
    possessor: type, /,
    context: _context.Context,
    annotations: __.cabc.Mapping[ str, __.typx.Any ],
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    for name, annotation in annotations.items( ):
        adjuncts = _interfaces.AdjunctsData( )
        annotation_ = reduce_annotation(
            annotation, context, adjuncts, cache )
        description = _compile_description( context, adjuncts, table )
        if not _is_attribute_visible(
            name, annotation_, context, adjuncts, description
        ): continue
        association = (
            _interfaces.AttributeAssociations.Class
            if 'ClassVar' in adjuncts.traits
            else _interfaces.AttributeAssociations.Instance )
        default = _determine_default_valuator( context, adjuncts )
        informations.append( _interfaces.AttributeInformation(
            name = name,
            annotation = annotation_,
            description = description,
            association = association,
            default = default ) )
    return informations


def _introspect_class_attributes(
    possessor: type, /,
    context: _context.Context,
    annotations: __.cabc.Mapping[ str, __.typx.Any ],
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    adjuncts = _interfaces.AdjunctsData( ) # dummy value
    for name, attribute in __.inspect.getmembers( possessor ):
        if name in annotations: continue # already processed
        if not _is_attribute_visible(
            name, _interfaces.absent, context, adjuncts, None
        ): continue
        if callable( attribute ): continue # separately documented
        informations.append( _interfaces.AttributeInformation(
            name = name,
            annotation = _interfaces.absent,
            description = None,
            association = _interfaces.AttributeAssociations.Class,
            default = _default_default ) )
    return informations


def _introspect_function(
    possessor: __.cabc.Callable[ ..., __.typx.Any ],
    context: _context.Context,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
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
            annotations, signature, context, cache, table ) )
    if 'return' in annotations:
        informations.extend( _introspect_function_return(
            annotations[ 'return' ], context, cache, table ) )
    return tuple( informations )


def _introspect_function_return(
    annotation: __.typx.Any,
    context: _context.Context,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    adjuncts = _interfaces.AdjunctsData( )
    annotation_ = reduce_annotation( annotation, context, adjuncts, cache )
    description = _compile_description( context, adjuncts, table )
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
    context: _context.Context,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.ArgumentInformation ]:
    informations: list[ _interfaces.ArgumentInformation ] = [ ]
    for name, param in signature.parameters.items( ):
        annotation = annotations.get( name, param.annotation )
        adjuncts = _interfaces.AdjunctsData( )
        if annotation is param.empty:
            annotation_ = _interfaces.absent
            description = None
        else:
            annotation_ = reduce_annotation(
                annotation, context, adjuncts, cache )
            description = _compile_description( context, adjuncts, table )
        if param.default is param.empty: default = _default_suppress
        else: default = _determine_default_valuator( context, adjuncts )
        informations.append( _interfaces.ArgumentInformation(
            name = name,
            annotation = annotation_,
            description = description,
            paramspec = param,
            default = default ) )
    return tuple( informations )


def _introspect_module(
    possessor: __.types.ModuleType,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    informations.extend( _introspect_module_annotations(
        possessor, context, annotations, cache, table ) )
    if introspection.module_control.scan_attributes:
        informations.extend( _introspect_module_attributes(
            possessor, context, annotations ) )
    return tuple( informations )


def _introspect_module_annotations(
    possessor: __.types.ModuleType, /,
    context: _context.Context,
    annotations: __.cabc.Mapping[ str, __.typx.Any ],
    cache: _interfaces.AnnotationsCache,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    for name, annotation in annotations.items( ):
        adjuncts = _interfaces.AdjunctsData( )
        annotation_ = reduce_annotation(
            annotation, context, adjuncts, cache )
        description = _compile_description( context, adjuncts, table )
        if not _is_attribute_visible(
            name, annotation_, context, adjuncts, description
        ): continue
        default = _determine_default_valuator( context, adjuncts )
        informations.append( _interfaces.AttributeInformation(
            name = name,
            annotation = annotation_,
            description = description,
            association = _interfaces.AttributeAssociations.Module,
            default = default ) )
    return informations


def _introspect_module_attributes(
    possessor: __.types.ModuleType, /,
    context: _context.Context,
    annotations: __.cabc.Mapping[ str, __.typx.Any ],
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    informations: list[ _interfaces.InformationBase ] = [ ]
    adjuncts = _interfaces.AdjunctsData( ) # dummy value
    attribute: object
    for name, attribute in __.inspect.getmembers( possessor ):
        if name in annotations: continue # already processed
        if not _is_attribute_visible(
            name, _interfaces.absent, context, adjuncts, None
        ): continue
        if callable( attribute ): continue # separately documented
        informations.append( _interfaces.AttributeInformation(
            name = name,
            annotation = _interfaces.absent,
            description = None,
            association = _interfaces.AttributeAssociations.Module,
            default = _default_default ) )
    return informations


def _is_attribute_visible(
    name: str,
    annotation: __.typx.Any,
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    description: __.typx.Optional[ str ],
) -> bool:
    visibility = next(
        (   extra for extra in adjuncts.extras
            if isinstance( extra, _interfaces.Visibilities ) ),
        _interfaces.Visibilities.Default )
    match visibility:
        case _interfaces.Visibilities.Conceal: return False
        case _interfaces.Visibilities.Reveal: return True
        case _:
            return context.visibility_decider( name, annotation, description )


def _reduce_annotation_arguments(
    origin: __.typx.Any,
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> __.cabc.Sequence[ __.typx.Any ]:
    if __.inspect.isclass( origin ) and issubclass( origin, __.cabc.Callable ):
        return _reduce_annotation_for_callable(
            arguments, context, adjuncts.copy( ), cache )
    return tuple(
        reduce_annotation( argument, context, adjuncts.copy( ), cache )
        for argument in arguments )


def _reduce_annotation_core(
    annotation: __.typx.Any,
    context: _context.Context,
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
        return reduce_annotation(
            annotation.__origin__, context, adjuncts, cache )
    return _filter_reconstitute_annotation(
        origin, arguments, context, adjuncts, cache )


def _reduce_annotation_for_callable(
    arguments: __.cabc.Sequence[ __.typx.Any ],
    context: _context.Context,
    adjuncts: _interfaces.AdjunctsData,
    cache: _interfaces.AnnotationsCache,
) -> tuple[ list[ __.typx.Any ] | __.types.EllipsisType, __.typx.Any ]:
    farguments, freturn = arguments
    if farguments is Ellipsis:
        farguments_r = Ellipsis
    else:
        farguments_r = [
            reduce_annotation( element, context, adjuncts.copy( ), cache )
            for element in farguments ]
    freturn_r = (
        reduce_annotation( freturn, context, adjuncts.copy( ), cache ) )
    return ( farguments_r, freturn_r )
