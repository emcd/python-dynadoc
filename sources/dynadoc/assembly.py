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
# TODO: assign_module_docstring
#       Recursion option for module tree of package.
#       Uses _decorate_module_members.


from __future__ import annotations

from . import __
from . import formatters as _formatters
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import nomina as _nomina
from . import notification as _notification


WithDocstringFragmentsArgument: __.typx.TypeAlias = __.typx.Annotated[
    _nomina.Fragment,
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


def produce_context(
    invoker_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_locals: __.typx.Optional[ _nomina.Variables ] = None,
    notifier: _interfaces.Notifier = _notification.notify,
    visibility_predicate: _interfaces.VisibilityPredicate = (
        _introspection.is_attribute_visible ),
) -> _interfaces.Context:
    return _interfaces.Context(
        notifier = notifier,
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


def _decorate( # noqa: PLR0913
    objct: _nomina.Documentable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    fragments: __.cabc.Sequence[ _nomina.Fragment ],
    table: _nomina.FragmentsTable,
) -> None:
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
    fragments: __.cabc.Sequence[ _nomina.Fragment ],
    table: _nomina.FragmentsTable,
) -> None:
    fragments_: list[ str ] = [ ]
    if preserve:
        fragment = __.inspect.getdoc( objct )
        if fragment: fragments_.append( fragment )
    fragments_.extend(
        (   fragment.documentation
            if isinstance( fragment, __.typx.Doc )
            else table[ fragment ] )
        for fragment in fragments )
    if introspect:
        cache = _interfaces.AnnotationsCache( )
        informations = (
            _introspection.introspect(
                objct, context = context, cache = cache ) )
        fragments_.append(
            formatter( objct, informations, context = context ) )
    docstring = '\n\n'.join(
        __.inspect.cleandoc( fragment ) for fragment in fragments_ )
    objct.__doc__ = docstring if docstring else None


def _decorate_class_attributes( # noqa: PLR0913
    objct: _nomina.Decoratable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    table: _nomina.FragmentsTable,
) -> None:
    predicate = (
        __.funct.partial(
            _is_decoratable_class_attribute,
            mname = objct.__module__, qname = objct.__qualname__ ) )
    members = __.inspect.getmembers( objct, predicate )
    for _, member in members:
        # TODO: Inspect '_dynadoc_fragments_' on attribute, if exists.
        _decorate(
            member,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse_into = recurse_into,
            fragments = ( ),
            table = table )


def _decorate_module_attributes( # noqa: PLR0913
    module: __.types.ModuleType, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse_into: _interfaces.RecursionTargets,
    table: _nomina.FragmentsTable,
) -> None:
    predicate = (
        __.funct.partial(
            _is_decoratable_module_attribute, mname = module.__name__ ) )
    members = __.inspect.getmembers( module, predicate )
    for _, member in members:
        # TODO: Inspect '_dynadoc_fragments_' on attribute, if exists.
        _decorate(
            member,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse_into = recurse_into,
            fragments = ( ),
            table = table )


def _is_decoratable_class_attribute( # noqa: PLR0911
    objct: object, mname: str, qname: str
) -> bool:
    # TODO: Consider 'recurse_into' flags.
    if not callable( objct ): return False
    mname_ = getattr( objct, '__module__', None )
    if mname_ and mname != mname_: return False
    qname_ = getattr( objct, '__qualname__', None )
    if qname_ and not qname_.startswith( f"{qname}." ): return False
    if __.inspect.isclass( objct ): return True
    if __.inspect.isfunction( objct ): return objct.__name__ != '<lambda>'
    if __.inspect.isbuiltin( objct ): return False
    # TODO: Handle method descriptors, etc....
    return False


def _is_decoratable_module_attribute( # noqa: PLR0911
    objct: object, mname: str
) -> bool:
    # TODO: Consider 'recurse_into' flags.
    if __.inspect.ismodule( objct ):
        return objct.__name__.startswith( f"{mname}." )
    if not callable( objct ): return False
    mname_ = getattr( objct, '__module__', None )
    if mname_ and mname != mname_: return False
    if __.inspect.isclass( objct ): return True
    if __.inspect.isfunction( objct ): return objct.__name__ != '<lambda>'
    if __.inspect.isbuiltin( objct ): return False
    return False
