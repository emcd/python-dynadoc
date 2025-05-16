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


from __future__ import annotations

from . import __
from . import formatters as _formatters
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import nomina as _nomina
from . import notification as _notification


WithDocstringFragmentsArgument: __.typx.TypeAlias = __.typx.Annotated[
    _interfaces.Fragment,
    __.typx.Doc(
        ''' Fragments from which to produce a docstring.

            If fragment is a string, then it will be used as an index
            into a table of docstring fragments.
            If fragment is a :pep:`727` ``Doc`` object, then the value of its
            ``documentation`` attribute will be incorporated.
        ''' ),
]
WithDocstringIntrospectArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.typx.Doc( ''' Introspect classes and functions? ''' )
]
WithDocstringPreserveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, __.typx.Doc( ''' Preserve extant docstring? ''' )
]
WithDocstringRecurseIntoArgument: __.typx.TypeAlias = __.typx.Annotated[
    _interfaces.RecursionTargets,
    __.typx.Doc( ''' Which kinds of objects to recursively document. ''' ),
]
WithDocstringTableArgument: __.typx.TypeAlias = __.typx.Annotated[
    _nomina.FragmentsTable,
    __.typx.Doc( ''' Table from which to copy docstring fragments. ''' ),
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
) -> _interfaces.Context:
    return _interfaces.Context(
        notifier = notifier,
        fragment_rectifier = fragment_rectifier,
        visibility_predicate = visibility_predicate,
        invoker_globals = invoker_globals,
        resolver_globals = resolver_globals,
        resolver_locals = resolver_locals )


context_default = produce_context( )
formatter_default = _formatters.sphinxrst.produce_fragment


def assign_module_docstring( # noqa: PLR0913
    module: _nomina.Module, /,
    *fragments: WithDocstringFragmentsArgument,
    context: _interfaces.Context = context_default,
    formatter: _interfaces.Formatter = formatter_default,
    introspect: WithDocstringIntrospectArgument = True,
    preserve: WithDocstringPreserveArgument = True,
    recurse_into: WithDocstringRecurseIntoArgument = (
        _interfaces.RecursionTargets.Null ),
    table: WithDocstringTableArgument = __.dictproxy_empty,
) -> None:
    ''' Assembles docstring from fragments and assigns it to module. '''
    if isinstance( module, str ):
        module = __.sys.modules[ module ]
    context_ = (
        context
        if not introspect or context.invoker_globals is not None
        else context.with_invoker_globals( ) )
    _decorate(
        module,
        context = context_,
        formatter = formatter,
        introspect = introspect,
        preserve = preserve,
        recurse_into = recurse_into,
        fragments = fragments,
        table = table )


def with_docstring( # noqa: PLR0913
    *fragments: WithDocstringFragmentsArgument,
    context: _interfaces.Context = context_default,
    formatter: _interfaces.Formatter = formatter_default,
    introspect: WithDocstringIntrospectArgument = True,
    preserve: WithDocstringPreserveArgument = True,
    recurse_into: WithDocstringRecurseIntoArgument = (
        _interfaces.RecursionTargets.Null ),
    table: WithDocstringTableArgument = __.dictproxy_empty,
) -> _nomina.Decorator[ _nomina.D ]:
    ''' Assembles docstring from fragments and decorates object with it. '''
    def decorate( objct: _nomina.D ) -> _nomina.D:
        context_ = (
            context
            if not introspect or context.invoker_globals is not None
            else context.with_invoker_globals( ) )
        _decorate(
            objct,
            context = context_,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse_into = recurse_into,
            fragments = fragments,
            table = table )
        return objct

    return decorate


def _check_module_recursion(
    objct: object, /, targets: _interfaces.RecursionTargets, mname: str
) -> __.typx.TypeIs[ __.types.ModuleType ]:
    if (    targets & _interfaces.RecursionTargets.Module
        and __.inspect.ismodule( objct )
    ): return objct.__name__.startswith( f"{mname}." )
    return False


def _collect_fragments(
    objct: _nomina.Documentable, /, context: _interfaces.Context, fqname: str
) -> _interfaces.Fragments:
    fragments: _interfaces.Fragments = (
        getattr( objct, context.fragments_name, ( ) ) )
    if not isinstance( fragments, __.cabc.Sequence ):
        emessage = f"Invalid fragments sequence on {fqname}."
        context.notifier( 'error', emessage )
        fragments = ( )
    return fragments


def _consider_class_attribute( # noqa: C901,PLR0913
    attribute: object, /,
    context: _interfaces.Context,
    targets: _interfaces.RecursionTargets,
    pmname: str, pqname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, targets, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_ and targets & _interfaces.RecursionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if not attribute_ and targets & _interfaces.RecursionTargets.Descriptor:
        if isinstance( attribute, property ) and attribute.fget:
            # Examine docstring and signature of getter method on property.
            attribute_ = attribute.fget
            update_surface = True
        # TODO: Apply custom processors from context.
        if __.inspect.isdatadescriptor( attribute ):
            # Ignore descriptors which we do not know how to handle.
            return None, False
    if not attribute_ and targets & _interfaces.RecursionTargets.Function:
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
    context: _interfaces.Context,
    targets: _interfaces.RecursionTargets,
    pmname: str, aname: str,
) -> tuple[ __.typx.Optional[ _nomina.Documentable ], bool ]:
    if _check_module_recursion( attribute, targets, pmname ):
        return attribute, False
    attribute_ = None
    update_surface = False
    if (    not attribute_ and targets & _interfaces.RecursionTargets.Class
        and __.inspect.isclass( attribute )
    ): attribute_ = attribute
    if (    not attribute_ and targets & _interfaces.RecursionTargets.Function
        and __.inspect.isfunction( attribute ) and aname != '<lambda>'
    ): attribute_ = attribute
    if attribute_:
        mname = getattr( attribute_, '__module__', None )
        if not mname or mname != pmname:
            attribute_ = None
    return attribute_, update_surface


def _decorate( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    if objct in _visitees: return # Prevent multiple decoration.
    _visitees.add( objct )
    if recurse_into:
        if __.inspect.isclass( objct ):
            _decorate_class_attributes(
                objct,
                context = context,
                formatter = formatter,
                introspect = introspect,
                preserve = preserve,
                recurse_into = recurse_into,
                table = table )
        elif __.inspect.ismodule( objct ):
            _decorate_module_attributes(
                objct,
                context = context,
                formatter = formatter,
                introspect = introspect,
                preserve = preserve,
                recurse_into = recurse_into,
                table = table )
    _decorate_core(
        objct,
        context = context,
        formatter = formatter,
        introspect = introspect,
        preserve = preserve,
        fragments = fragments,
        table = table )


def _decorate_core( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    fragments: _interfaces.Fragments,
    table: _nomina.FragmentsTable,
) -> None:
    fragments_: list[ str ] = [ ]
    if preserve:
        fragment = __.inspect.getdoc( objct )
        if fragment: fragments_.append( fragment )
    fragments_.extend(
        context.fragment_rectifier(
            fragment.documentation
            if isinstance( fragment, _interfaces.Doc )
            else table[ fragment ] )
        for fragment in fragments )
    if introspect:
        cache = _interfaces.AnnotationsCache( )
        informations = (
            _introspection.introspect(
                objct, context = context, cache = cache, table = table ) )
        fragments_.append(
            formatter( objct, informations, context = context ) )
    docstring = '\n\n'.join(
        fragment for fragment in filter( None, fragments_ ) ).rstrip( )
    objct.__doc__ = docstring if docstring else None


def _decorate_class_attributes( # noqa: PLR0913
    objct: type, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = objct.__module__
    pqname = objct.__qualname__
    for aname, attribute, surface_attribute in (
        _survey_class_attributes( objct, context, recurse_into )
    ):
        fqname = f"{pmname}.{pqname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        _decorate(
            attribute,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse_into = recurse_into,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _decorate_module_attributes( # noqa: PLR0913
    module: __.types.ModuleType, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    table: _nomina.FragmentsTable,
) -> None:
    pmname = module.__name__
    for aname, attribute, surface_attribute in (
        _survey_module_attributes( module, context, recurse_into )
    ):
        fqname = f"{pmname}.{aname}"
        fragments = _collect_fragments( attribute, context, fqname )
        _decorate(
            attribute,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse_into = recurse_into,
            fragments = fragments,
            table = table )
        if attribute is not surface_attribute:
            surface_attribute.__doc__ = attribute.__doc__


def _survey_class_attributes(
    possessor: type, /,
    context: _interfaces.Context,
    targets: _interfaces.RecursionTargets,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__module__
    pqname = possessor.__qualname__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_class_attribute(
                attribute, context, targets, pmname, pqname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_


def _survey_module_attributes(
    possessor: __.types.ModuleType, /,
    context: _interfaces.Context,
    targets: _interfaces.RecursionTargets,
) -> __.cabc.Iterator[ tuple[ str, _nomina.Documentable, object ] ]:
    pmname = possessor.__name__
    for aname, attribute in __.inspect.getmembers( possessor ):
        attribute_, update_surface = (
            _consider_module_attribute(
                attribute, context, targets, pmname, aname ) )
        if attribute_ is None: continue
        if update_surface:
            yield aname, attribute_, attribute
            continue
        yield aname, attribute_, attribute_
