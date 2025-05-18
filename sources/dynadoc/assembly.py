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


''' Docstring assembly. '''
# TODO? with_docstring_defer
#       Registers with_docstring partial function in registry.
#       Registry can be executed after modules are loaded and all string
#       annotations should be resolvable.


from . import __
from . import context as _context
from . import formatters as _formatters
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import nomina as _nomina
from . import notification as _notification


class Formatter( __.typx.Protocol ):
    ''' Formatter for arguments, attributes, exceptions, and returns. '''

    @staticmethod
    def __call__(
        possessor: _nomina.Documentable,
        informations: _interfaces.Informations,
        context: _context.Context,
    ) -> str: raise NotImplementedError


WithDocstringFragmentsArgument: __.typx.TypeAlias = __.typx.Annotated[
    _interfaces.Fragment,
    _interfaces.Doc(
        ''' Fragments from which to produce a docstring.

            If fragment is a string, then it will be used as an index
            into a table of docstring fragments.
            If fragment is a :pep:`727` ``Doc`` object, then the value of its
            ``documentation`` attribute will be incorporated.
        ''' ),
]
WithDocstringIntrospectArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, _interfaces.Doc( ''' Introspect classes and functions? ''' )
]
WithDocstringPreserveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, _interfaces.Doc( ''' Preserve extant docstring? ''' )
]
WithDocstringRecursionArgument: __.typx.TypeAlias = __.typx.Annotated[
    _context.RecursionControl,
    _interfaces.Doc( ''' How to handle recursion. ''' ),
]
WithDocstringTableArgument: __.typx.TypeAlias = __.typx.Annotated[
    _nomina.FragmentsTable,
    _interfaces.Doc( ''' Table from which to copy docstring fragments. ''' ),
]


_visitees: __.weakref.WeakSet[ _nomina.Documentable ] = __.weakref.WeakSet( )


def produce_context( # noqa: PLR0913
    invoker_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_locals: __.typx.Optional[ _nomina.Variables ] = None,
    notifier: _interfaces.Notifier = _notification.notify,
    fragment_rectifier: _interfaces.FragmentRectifier = (
        lambda fragment: fragment ),
    visibility_predicate: _interfaces.VisibilityPredicate = (
        _introspection.is_attribute_visible ),
) -> _context.Context:
    # TODO: Move to factories module.
    # TODO: Document.
    return _context.Context(
        notifier = notifier,
        fragment_rectifier = fragment_rectifier,
        visibility_predicate = visibility_predicate,
        invoker_globals = invoker_globals,
        resolver_globals = resolver_globals,
        resolver_locals = resolver_locals )


context_default = produce_context( )
formatter_default = _formatters.sphinxrst.produce_fragment
recursion_default = _context.RecursionControl( )


def assign_module_docstring( # noqa: PLR0913
    module: _nomina.Module, /,
    *fragments: WithDocstringFragmentsArgument,
    context: _context.Context = context_default,
    formatter: Formatter = formatter_default,
    introspect: WithDocstringIntrospectArgument = True,
    preserve: WithDocstringPreserveArgument = True,
    recursion: WithDocstringRecursionArgument = recursion_default,
    table: WithDocstringTableArgument = __.dictproxy_empty,
) -> None:
    # TODO: Move to decorators module.
    ''' Assembles docstring from fragments and assigns it to module. '''
    if isinstance( module, str ):
        module = __.sys.modules[ module ]
    _decorate(
        module,
        context = context,
        formatter = formatter,
        introspect = introspect,
        preserve = preserve,
        recursion = recursion,
        fragments = fragments,
        table = table )


def with_docstring( # noqa: PLR0913
    *fragments: WithDocstringFragmentsArgument,
    context: _context.Context = context_default,
    formatter: Formatter = formatter_default,
    introspect: WithDocstringIntrospectArgument = True,
    preserve: WithDocstringPreserveArgument = True,
    recursion: WithDocstringRecursionArgument = recursion_default,
    table: WithDocstringTableArgument = __.dictproxy_empty,
) -> _nomina.Decorator[ _nomina.D ]:
    # TODO: Move to decorators module.
    ''' Assembles docstring from fragments and decorates object with it. '''
    def decorate( objct: _nomina.D ) -> _nomina.D:
        _decorate(
            objct,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recursion = recursion,
            fragments = fragments,
            table = table )
        return objct

    return decorate


def _check_module_recursion(
    objct: object, /, recursion: _context.RecursionControl, mname: str
) -> __.typx.TypeIs[ __.types.ModuleType ]:
    if (    recursion.targets & _context.RecursionTargets.Module
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
    recursion: _context.RecursionControl,
    pmname: str, pqname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, recursion, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_
        and recursion.targets & _context.RecursionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if (    not attribute_
        and recursion.targets & _context.RecursionTargets.Descriptor
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
        and recursion.targets & _context.RecursionTargets.Function
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
    recursion: _context.RecursionControl,
    pmname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, recursion, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_
        and recursion.targets & _context.RecursionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if (    not attribute_
        and recursion.targets & _context.RecursionTargets.Function
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
    formatter: Formatter,
    introspect: bool,
    preserve: bool,
    recursion: _context.RecursionControl,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    if objct in _visitees: return # Prevent multiple decoration.
    _visitees.add( objct )
    if recursion.targets:
        if __.inspect.isclass( objct ):
            _decorate_class_attributes(
                objct,
                context = context,
                formatter = formatter,
                introspect = introspect,
                preserve = preserve,
                recursion = recursion,
                table = table )
        elif __.inspect.ismodule( objct ):
            _decorate_module_attributes(
                objct,
                context = context,
                formatter = formatter,
                introspect = introspect,
                preserve = preserve,
                recursion = recursion,
                table = table )
    _decorate_core(
        objct,
        context = context,
        formatter = formatter,
        introspect = introspect,
        preserve = preserve,
        recursion = recursion,
        fragments = fragments,
        table = table )


def _decorate_core( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _context.Context,
    formatter: Formatter,
    introspect: bool,
    preserve: bool,
    recursion: _context.RecursionControl,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    fragments_: list[ str ] = [ ]
    if preserve:
        fragment = __.inspect.getdoc( objct )
        if fragment: fragments_.append( fragment )
    fragments_.extend(
        _process_fragments_argument( context, fragments, table ) )
    if introspect:
        cache = _interfaces.AnnotationsCache( )
        informations = (
            _introspection.introspect(
                objct,
                context = context, recursion = recursion,
                cache = cache, table = table ) )
        fragments_.append(
            formatter( objct, informations, context = context ) )
    docstring = '\n\n'.join(
        fragment for fragment in filter( None, fragments_ ) ).rstrip( )
    objct.__doc__ = docstring if docstring else None


def _decorate_class_attributes( # noqa: PLR0913
    objct: type, /,
    context: _context.Context,
    formatter: Formatter,
    introspect: bool,
    preserve: bool,
    recursion: _context.RecursionControl,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = objct.__module__
    pqname = objct.__qualname__
    for aname, attribute, surface_attribute in (
        _survey_class_attributes( objct, context, recursion )
    ):
        fqname = f"{pmname}.{pqname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        recursion_ = _limit_recursion( attribute, context, recursion, fqname )
        recursion_ = recursion_.evaluate_limits_for( attribute )
        _decorate(
            attribute,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recursion = recursion_,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _decorate_module_attributes( # noqa: PLR0913
    module: __.types.ModuleType, /,
    context: _context.Context,
    formatter: Formatter,
    introspect: bool,
    preserve: bool,
    recursion: _context.RecursionControl,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = module.__name__
    for aname, attribute, surface_attribute in (
        _survey_module_attributes( module, context, recursion )
    ):
        fqname = f"{pmname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        recursion_ = _limit_recursion( attribute, context, recursion, fqname )
        recursion_ = recursion_.evaluate_limits_for( attribute )
        _decorate(
            attribute,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recursion = recursion_,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _limit_recursion(
    objct: _nomina.Documentable, /,
    context: _context.Context,
    recursion: _context.RecursionControl,
    fqname: str,
) -> _context.RecursionControl:
    limit: _context.RecursionLimit = (
        getattr(
            objct,
            context.recursion_limit_name,
            _context.RecursionLimit( ) ) )
    if not isinstance( limit, _context.RecursionLimit ):
        emessage = f"Invalid recursion limit on {fqname}: {limit!r}"
        context.notifier( 'error', emessage )
        return recursion
    return recursion.with_limit( limit )


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
    recursion: _context.RecursionControl,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__module__
    pqname = possessor.__qualname__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_class_attribute(
                attribute, context, recursion, pmname, pqname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_


def _survey_module_attributes(
    possessor: __.types.ModuleType, /,
    context: _context.Context,
    recursion: _context.RecursionControl,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__name__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_module_attribute(
                attribute, context, recursion, pmname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_
