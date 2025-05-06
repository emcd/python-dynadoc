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


''' Catalog of common type aliases. '''


from __future__ import annotations

from . import __


Decoratable: __.typx.TypeAlias = type | __.cabc.Callable[ ..., __.typx.Any ]
ClassDecorator: __.typx.TypeAlias = __.cabc.Callable[ [ type ], type ]
FunctionDecorator: __.typx.TypeAlias = (
    __.cabc.Callable[
        [ __.cabc.Callable[ ..., __.typx.Any ] ],
        __.cabc.Callable[ ..., __.typx.Any ] ] )
Decorator: __.typx.TypeAlias = ClassDecorator | FunctionDecorator
Fragment: __.typx.TypeAlias = str |  __.typx.Doc
FragmentsTable: __.typx.TypeAlias = __.cabc.Mapping[ str, str ]
NotificationLevels: __.typx.TypeAlias = (
    __.typx.Literal[ 'admonition', 'error', 'alert' ] )
Typle: __.typx.TypeAlias = __.cabc.Sequence[ __.typx.TypeForm[ __.typx.Any ] ]
Variables: __.typx.TypeAlias = __.cabc.Mapping[ str, __.typx.Any ]

WithDocstringFragmentsArgument: __.typx.TypeAlias = __.typx.Annotated[
    Fragment,
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
WithDocstringTableArgument: __.typx.TypeAlias = __.typx.Annotated[
    FragmentsTable,
    __.typx.Doc( ''' Table from which to copy docstring fragments. ''' ),
]
