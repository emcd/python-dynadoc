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


''' Factories and registries. '''
# TODO? Registry for deferred decoration.


from . import __
from . import context as _context
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import nomina as _nomina
from . import notification as _notification


def produce_context( # noqa: PLR0913
    invoker_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_globals: __.typx.Optional[ _nomina.Variables ] = None,
    resolver_locals: __.typx.Optional[ _nomina.Variables ] = None,
    notifier: _interfaces.Notifier = _notification.notify,
    fragment_rectifier: _interfaces.FragmentRectifier = (
        lambda fragment: fragment ),
    visibility_decider: _interfaces.VisibilityDecider = (
        _introspection.is_attribute_visible ),
) -> _context.Context:
    # TODO: Document.
    return _context.Context(
        notifier = notifier,
        fragment_rectifier = fragment_rectifier,
        visibility_decider = visibility_decider,
        invoker_globals = invoker_globals,
        resolver_globals = resolver_globals,
        resolver_locals = resolver_locals )
