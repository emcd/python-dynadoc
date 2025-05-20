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


''' Interface for extension development. '''

# ruff: noqa: F403,F405


from . import __

from .context import *
from .interfaces import *
from .introspection import *
from .nomina import *
from .notification import *


ContextArgument: __.typx.TypeAlias = __.typx.Annotated[
    Context, Fname( 'context' )
]
FragmentsArgumentMultivalent: __.typx.TypeAlias = __.typx.Annotated[
    Fragment,
    Doc(
        ''' Fragments from which to produce a docstring.

            If fragment is a string, then it will be used as an index
            into a table of docstring fragments.
            If fragment is a :pep:`727` ``Doc`` object, then the value of its
            ``documentation`` attribute will be incorporated.
        ''' ),
]
FragmentRectifierArgument: __.typx.TypeAlias = __.typx.Annotated[
    FragmentRectifier,
    Doc( ''' Cleans and normalizes docstring fragments. ''' ),
]
InformationsArgument: __.typx.TypeAlias = __.typx.Annotated[
    Informations,
    Doc( ''' Information extracted from object introspection. ''' ),
]
IntrospectionArgument: __.typx.TypeAlias = __.typx.Annotated[
    IntrospectionControl, Fname( 'introspection' )
]
InvokerGlobalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Variables ],
    Doc(
        ''' Dictionary of globals from the frame of a caller.

            Used by renderers for determing whether to fully-qualify a name.
        ''' ),
]
NotifierArgument: __.typx.TypeAlias = __.typx.Annotated[
    Notifier, Doc( ''' Notifies of warnings and errors. ''' ),
]
PossessorArgument: __.typx.TypeAlias = __.typx.Annotated[
    Documentable, Doc( ''' Object being documented. ''' ),
]
PreserveArgument: __.typx.TypeAlias = __.typx.Annotated[
    bool, Doc( ''' Preserve extant docstring? ''' )
]
RendererArgument: __.typx.TypeAlias = __.typx.Annotated[
    'Renderer', Fname( 'renderer' )
]
ResolverGlobalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Variables ],
    Doc(
        ''' Dictionary of globals for annotation resolution.

            Used for resolving string annotations.
        ''' ),
]
ResolverLocalsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.typx.Optional[ Variables ],
    Doc(
        ''' Dictionary of locals for annotation resolution.

            Used for resolving string annotations.
        ''' ),
]
TableArgument: __.typx.TypeAlias = __.typx.Annotated[
    FragmentsTable,
    Doc( ''' Table from which to copy docstring fragments. ''' ),
]
VisibilityDeciderArgument: __.typx.TypeAlias = __.typx.Annotated[
    VisibilityDecider,
    Doc( ''' Determines if an attribute should be documented. ''' ),
]


RendererReturnValue: __.typx.TypeAlias = __.typx.Annotated[
    str, Doc( ''' Rendered docstring fragment. ''' )
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
