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


''' Docstring assembly and decoration. '''
# TODO? with_docstring_defer
#       Registers with_docstring partial function in registry.
#       Registry can be executed after modules are loaded and all string
#       annotations should be resolvable.


from . import __
from . import context as _context
from . import factories as _factories
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import nomina as _nomina
from . import renderers as _renderers


ContextArgument: __.typx.TypeAlias = __.typx.Annotated[
    _context.Context, _interfaces.Fname( 'context' )
]
FragmentsArgumentMultivalent: __.typx.TypeAlias = __.typx.Annotated[
    _interfaces.Fragment,
    _interfaces.Doc(
        ''' Fragments from which to produce a docstring.

            If fragment is a string, then it will be used as an index
            into a table of docstring fragments.
            If fragment is a :pep:`727` ``Doc`` object, then the value of its
            ``documentation`` attribute will be incorporated.
        ''' ),
]
InformationsArgument: __.typx.TypeAlias = __.typx.Annotated[
    _interfaces.Informations,
    _interfaces.Doc(
        ''' Information extracted from object introspection. ''' ),
]
IntrospectionArgument: __.typx.TypeAlias = __.typx.Annotated[
    _context.IntrospectionControl, _interfaces.Fname( 'introspection' )
]
PossessorArgument: __.typx.TypeAlias = __.typx.Annotated[
    _nomina.Documentable,
    _interfaces.Doc( ''' Object being documented. ''' ),
]
PreserveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, _interfaces.Doc( ''' Preserve extant docstring? ''' )
]
RendererArgument: __.typx.TypeAlias = __.typx.Annotated[
    'Renderer', _interfaces.Fname( 'renderer' )
]
TableArgument: __.typx.TypeAlias = __.typx.Annotated[
    _nomina.FragmentsTable,
    _interfaces.Doc( ''' Table from which to copy docstring fragments. ''' ),
]

RendererReturnValue: __.typx.TypeAlias = __.typx.Annotated[
    str, _interfaces.Doc( ''' Rendered docstring fragment. ''' )
]
class Renderer( __.typx.Protocol ):
    ''' (Protocol for fragment renderer.) '''

    _dynadoc_fragments_ = ( 'renderer', )

    @staticmethod
    def __call__(
        possessor: PossessorArgument,
        informations: InformationsArgument,
        context: ContextArgument,
    ) -> RendererReturnValue:
        ''' (Signature for fragment renderer.) '''
        raise NotImplementedError


_visitees: __.weakref.WeakSet[ _nomina.Documentable ] = __.weakref.WeakSet( )


context_default: __.typx.Annotated[
    _context.Context,
    _interfaces.Doc(
        ''' Default context for introspection and rendering. ''' ),
    _interfaces.Fname( 'context' ),
    _interfaces.Default( mode = _interfaces.ValuationModes.Suppress ),
] = _factories.produce_context( )
introspection_default: __.typx.Annotated[
    _context.IntrospectionControl,
    _interfaces.Doc( ''' Default introspection control. ''' ),
    _interfaces.Fname( 'introspection' ),
    _interfaces.Default( mode = _interfaces.ValuationModes.Suppress ),
] = _context.IntrospectionControl( )
renderer_default: __.typx.Annotated[
    Renderer,
    _interfaces.Doc( ''' Default renderer for docstring fragments. ''' ),
    _interfaces.Fname( 'renderer' ),
    _interfaces.Default( mode = _interfaces.ValuationModes.Suppress ),
] = __.typx.cast( Renderer, _renderers.sphinxad.produce_fragment )


def assign_module_docstring( # noqa: PLR0913
    module: _nomina.Module, /,
    *fragments: FragmentsArgumentMultivalent,
    context: ContextArgument = context_default,
    introspection: IntrospectionArgument = introspection_default,
    preserve: PreserveArgument = True,
    renderer: RendererArgument = renderer_default,
    table: TableArgument = __.dictproxy_empty,
) -> None:
    ''' Assembles docstring from fragments and assigns it to module. '''
    if isinstance( module, str ):
        module = __.sys.modules[ module ]
    _decorate(
        module,
        context = context,
        introspection = introspection,
        preserve = preserve,
        renderer = renderer,
        fragments = fragments,
        table = table )


def with_docstring(
    *fragments: FragmentsArgumentMultivalent,
    context: ContextArgument = context_default,
    introspection: IntrospectionArgument = introspection_default,
    preserve: PreserveArgument = True,
    renderer: RendererArgument = renderer_default,
    table: TableArgument = __.dictproxy_empty,
) -> _nomina.Decorator[ _nomina.D ]:
    ''' Assembles docstring from fragments and decorates object with it. '''
    def decorate( objct: _nomina.D ) -> _nomina.D:
        _decorate(
            objct,
            context = context,
            introspection = introspection,
            preserve = preserve,
            renderer = renderer,
            fragments = fragments,
            table = table )
        return objct

    return decorate


def _check_module_recursion(
    objct: object, /,
    introspection: _context.IntrospectionControl,
    mname: str
) -> __.typx.TypeIs[ __.types.ModuleType ]:
    if (    introspection.targets & _context.IntrospectionTargets.Module
        and __.inspect.ismodule( objct )
    ): return objct.__name__.startswith( f"{mname}." )
    return False


def _collect_fragments(
    objct: _nomina.Documentable, /, context: _context.Context, fqname: str
) -> _interfaces.Fragments:
    fragments: _interfaces.Fragments = (
        getattr( objct, context.fragments_name, ( ) ) )
    if not isinstance( fragments, __.cabc.Sequence ):
        emessage = f"Invalid fragments sequence on {fqname}: {fragments!r}"
        context.notifier( 'error', emessage )
        fragments = ( )
    for fragment in fragments:
        if not isinstance( fragment, ( str, _interfaces.Doc ) ):
            emessage = f"Invalid fragment on {fqname}: {fragment!r}"
            context.notifier( 'error', emessage )
    return fragments


def _consider_class_attribute( # noqa: C901,PLR0913
    attribute: object, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    pmname: str, pqname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, introspection, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_
        and introspection.targets & _context.IntrospectionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if (    not attribute_
        and introspection.targets & _context.IntrospectionTargets.Descriptor
    ):
        if isinstance( attribute, property ) and attribute.fget:
            # Examine docstring and signature of getter method on property.
            attribute_ = attribute.fget
            update_surface = True
        # TODO: Apply custom processors from context.
        if __.inspect.isdatadescriptor( attribute ):
            # Ignore descriptors which we do not know how to handle.
            return None, False
    if (    not attribute_
        and introspection.targets & _context.IntrospectionTargets.Function
    ):
        if __.inspect.ismethod( attribute ):
            # Methods proxy docstrings from their core functions.
            attribute_ = attribute.__func__
        if __.inspect.isfunction( attribute ) and aname != '<lambda>':
            attribute_ = attribute
    if attribute_:
        mname = getattr( attribute_, '__module__', None )
        if not mname or mname != pmname:
            attribute_ = None
    if attribute_:
        qname = getattr( attribute_, '__qualname__', None )
        if not qname or not qname.startswith( f"{pqname}." ):
            attribute_ = None
    return attribute_, update_surface


def _consider_module_attribute(
    attribute: object, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    pmname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, introspection, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_
        and introspection.targets & _context.IntrospectionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if (    not attribute_
        and introspection.targets & _context.IntrospectionTargets.Function
        and __.inspect.isfunction( attribute ) and aname != '<lambda>'
    ): attribute_ = attribute
    if attribute_:
        mname = getattr( attribute_, '__module__', None )
        if not mname or mname != pmname:
            attribute_ = None
    return attribute_, update_surface


def _decorate( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    preserve: bool,
    renderer: Renderer,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    if objct in _visitees: return # Prevent multiple decoration.
    _visitees.add( objct )
    if introspection.targets:
        if __.inspect.isclass( objct ):
            _decorate_class_attributes(
                objct,
                context = context,
                introspection = introspection,
                preserve = preserve,
                renderer = renderer,
                table = table )
        elif __.inspect.ismodule( objct ):
            _decorate_module_attributes(
                objct,
                context = context,
                introspection = introspection,
                preserve = preserve,
                renderer = renderer,
                table = table )
    _decorate_core(
        objct,
        context = context,
        introspection = introspection,
        preserve = preserve,
        renderer = renderer,
        fragments = fragments,
        table = table )


def _decorate_core( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    preserve: bool,
    renderer: Renderer,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    fragments_: list[ str ] = [ ]
    if preserve:
        fragment = __.inspect.getdoc( objct )
        if fragment: fragments_.append( fragment )
    fragments_.extend(
        _process_fragments_argument( context, fragments, table ) )
    if introspection.enable:
        cache = _interfaces.AnnotationsCache( )
        informations = (
            _introspection.introspect(
                objct,
                context = context, introspection = introspection,
                cache = cache, table = table ) )
        fragments_.append(
            renderer( objct, informations, context = context ) )
    docstring = '\n\n'.join(
        fragment for fragment in filter( None, fragments_ ) ).rstrip( )
    objct.__doc__ = docstring if docstring else None


def _decorate_class_attributes( # noqa: PLR0913
    objct: type, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    preserve: bool,
    renderer: Renderer,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = objct.__module__
    pqname = objct.__qualname__
    for aname, attribute, surface_attribute in (
        _survey_class_attributes( objct, context, introspection )
    ):
        fqname = f"{pmname}.{pqname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        introspection_ = _limit_introspection(
            attribute, context, introspection, fqname )
        introspection_ = introspection_.evaluate_limits_for( attribute )
        _decorate(
            attribute,
            context = context,
            introspection = introspection_,
            preserve = preserve,
            renderer = renderer,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _decorate_module_attributes( # noqa: PLR0913
    module: __.types.ModuleType, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    preserve: bool,
    renderer: Renderer,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = module.__name__
    for aname, attribute, surface_attribute in (
        _survey_module_attributes( module, context, introspection )
    ):
        fqname = f"{pmname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        introspection_ = _limit_introspection(
            attribute, context, introspection, fqname )
        introspection_ = introspection_.evaluate_limits_for( attribute )
        _decorate(
            attribute,
            context = context,
            introspection = introspection_,
            preserve = preserve,
            renderer = renderer,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _limit_introspection(
    objct: _nomina.Documentable, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
    fqname: str,
) -> _context.IntrospectionControl:
    limit: _context.IntrospectionLimit = (
        getattr(
            objct,
            context.introspection_limit_name,
            _context.IntrospectionLimit( ) ) )
    if not isinstance( limit, _context.IntrospectionLimit ):
        emessage = f"Invalid introspection limit on {fqname}: {limit!r}"
        context.notifier( 'error', emessage )
        return introspection
    return introspection.with_limit( limit )


def _process_fragments_argument(
    context: _context.Context,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> __.cabc.Sequence[ str ]:
    fragments_: list[ str ] = [ ]
    for fragment in fragments:
        if isinstance( fragment, _interfaces.Doc ):
            fragment_r = fragment.documentation
        elif isinstance( fragment, str ):
            if fragment not in table:
                emessage = f"Fragment '{fragment}' not in provided table."
                context.notifier( 'error', emessage )
            else: fragment_r = table[ fragment ]
        else:
            emessage = f"Fragment {fragment!r} is invalid. Must be Doc or str."
            context.notifier( 'error', emessage )
            continue
        fragments_.append( context.fragment_rectifier( fragment_r ) )
    return fragments_


def _survey_class_attributes(
    possessor: type, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__module__
    pqname = possessor.__qualname__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_class_attribute(
                attribute, context, introspection, pmname, pqname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_


def _survey_module_attributes(
    possessor: __.types.ModuleType, /,
    context: _context.Context,
    introspection: _context.IntrospectionControl,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__name__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_module_attribute(
                attribute, context, introspection, pmname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_
