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


def with_docstring(
    *fragments: _nomina.WithDocstringFragmentsArgument,
    context: _interfaces.Context = context_default,
    formatter: _interfaces.Formatter = formatter_default,
    introspect: _nomina.WithDocstringIntrospectArgument = True,
    preserve: _nomina.WithDocstringPreserveArgument = True,
    table: _nomina.WithDocstringTableArgument = __.dictproxy_empty,
) -> _nomina.Decorator:
    ''' Assembles docstring from fragments and decorates object with it. '''
    def decorate( objct: _nomina.Decoratable ) -> _nomina.Decoratable:
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
            context_ = (
                context if context.invoker_globals is not None
                else context.with_invoker_globals( ) )
            informations = (
                _introspection.introspect(
                    objct, context = context_, cache = cache ) )
            fragments_.append(
                formatter( objct, informations, context = context_ ) )
        docstring = '\n\n'.join(
            __.inspect.cleandoc( fragment ) for fragment in fragments_ )
        objct.__doc__ = docstring if docstring else None
        return objct

    return decorate


_context = produce_context( notifier = _notification.notify_internal )
with_docstring( context = _context )( with_docstring ) # pyright: ignore[reportArgumentType]
