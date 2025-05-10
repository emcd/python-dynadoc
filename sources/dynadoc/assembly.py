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


def with_docstring( # noqa: PLR0913
    *fragments: _nomina.WithDocstringFragmentsArgument,
    context: _interfaces.Context = context_default,
    formatter: _interfaces.Formatter = formatter_default,
    introspect: _nomina.WithDocstringIntrospectArgument = True,
    preserve: _nomina.WithDocstringPreserveArgument = True,
    recurse: _nomina.WithDocstringRecurseArgument = False,
    table: _nomina.WithDocstringTableArgument = __.dictproxy_empty,
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
            recurse = recurse,
            fragments = fragments,
            table = table )
        return objct

    return decorate


def _decorate( # noqa: PLR0913
    objct: _nomina.Decoratable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    recurse: bool,
    fragments: __.cabc.Sequence[ _nomina.Fragment ],
    table: _nomina.FragmentsTable,
) -> None:
    if recurse and __.inspect.isclass( objct ):
        _decorate_class_members(
            objct,
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            table = table )
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


def _decorate_class_members( # noqa: PLR0913
    objct: _nomina.Decoratable, /,
    context: _interfaces.Context,
    formatter: _interfaces.Formatter,
    introspect: bool,
    preserve: bool,
    table: _nomina.FragmentsTable,
) -> None:
    predicate = (
        __.funct.partial(
            _is_interior_decoratable,
            mname = objct.__module__, qname = objct.__qualname__ ) )
    members = __.inspect.getmembers( objct, predicate )
    for _, member in members:
        # TODO: Get fragments from '_dynadoc_fragments_' on member, if exists.
        with_docstring(
            context = context,
            formatter = formatter,
            introspect = introspect,
            preserve = preserve,
            recurse = True,
            table = table )( member )


def _is_interior_decoratable( # noqa: PLR0911
    objct: object, mname: str, qname: str
) -> bool:
    if not callable( objct ): return False
    mname_ = getattr( objct, '__module__', None )
    if mname_ and mname != mname_: return False
    qname_ = getattr( objct, '__qualname__', None )
    if qname_ and not qname_.startswith( f"{qname}." ): return False
    if __.inspect.isclass( objct ): return True
    if __.inspect.isfunction( objct ): return objct.__name__ != '<lambda>'
    if __.inspect.isbuiltin( objct ): return False
    # TODO: Handle method descriptors, etc....
    print( f"{objct=}" )
    return False
