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
from . import xtnsapi as _xtnsapi


InvokerGlobalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ _xtnsapi.Variables ],
    _xtnsapi.Doc(
        ''' Dictionary of globals from the frame of a caller.

            Used by renderers for determing whether to fully-qualify a name.
        ''' ),
]
ResolverGlobalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ _xtnsapi.Variables ],
    _xtnsapi.Doc(
        ''' Dictionary of globals for annotation resolution.

            Used for resolving string annotations.
        ''' ),
]
ResolverLocalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ _xtnsapi.Variables ],
    _xtnsapi.Doc(
        ''' Dictionary of locals for annotation resolution.

            Used for resolving string annotations.
        ''' ),
]
NotifierArgument: __.typx.TypeAlias = __.typx.Annotated[
    _xtnsapi.Notifier,
    _xtnsapi.Doc( ''' Callback for notification of warnings and errors. ''' ),
]
FragmentRectifierArgument: __.typx.TypeAlias = __.typx.Annotated[
    _xtnsapi.FragmentRectifier,
    _xtnsapi.Doc(
        ''' Function to clean and normalize docstring fragments. ''' ),
]
VisibilityDeciderArgument: __.typx.TypeAlias = __.typx.Annotated[
    _xtnsapi.VisibilityDecider,
    _xtnsapi.Doc(
        ''' Function to determine if an attribute should be documented. ''' ),
]


def produce_context( # noqa: PLR0913
    invoker_globals: InvokerGlobalsArgument = None,
    resolver_globals: ResolverGlobalsArgument = None,
    resolver_locals: ResolverLocalsArgument = None,
    notifier: NotifierArgument = _xtnsapi.notify,
    fragment_rectifier: FragmentRectifierArgument = (
        lambda fragment: fragment ),
    visibility_decider: VisibilityDeciderArgument = (
        _xtnsapi.is_attribute_visible ),
) -> _xtnsapi.Context:
    ''' Creates context data transfer object.

        Reasonable defaults are used for arguments that are not supplied.

        The context is for annotation evaluation and docstring generation.
        Controls how annotations are resolved, how fragments are processed,
        and how notifications are issued.

        The globals and locals dictionaries are used for resolving annotations
        that are specified as strings. If not provided, annotations will be
        resolved in the context where they are evaluated.
    '''
    return _xtnsapi.Context(
        notifier = notifier,
        fragment_rectifier = fragment_rectifier,
        visibility_decider = visibility_decider,
        invoker_globals = invoker_globals,
        resolver_globals = resolver_globals,
        resolver_locals = resolver_locals )
