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


''' Public interfaces for formatters, etc.... '''


from __future__ import annotations

# Note: Can replace typx.Doc with an equivalent in the future,
#       if support for it disappears from typing extensions.
from typing_extensions import Doc # noqa: F401

from . import __
from . import nomina as _nomina


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Raises:
    ''' Class and description of exception that can be raised. '''

    classes: type[ BaseException ] | __.cabc.Sequence[ type[ BaseException ] ]
    description: __.typx.Optional[ str ] = None


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class AdjunctsData:
    ''' Data about type-adjacent entities. '''

    extras: __.cabc.MutableSequence[ __.typx.Any ] = (
        __.dcls.field( default_factory = list[ __.typx.Any ] ) )
    traits: __.cabc.MutableSet[ str ] = (
        __.dcls.field( default_factory = set[ str ] ) )

    def copy( self ) -> __.typx.Self:
        return type( self )(
            extras = list( self.extras ),
            traits = set( self.traits ) )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' Context for annotation evaluation, etc.... '''

    notifier: Notifier
    localvars: __.typx.Optional[ _nomina.Variables ] = None
    globalvars: __.typx.Optional[ _nomina.Variables ] = None


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class InformationBase:
    ''' Base for information on various kinds of entities. '''

    typeform: __.typx.Any
    description: __.typx.Optional[ str ]


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ArgumentInformation( InformationBase ):

    name: str
    paramspec: __.inspect.Parameter


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class AttributeInformation( InformationBase ):

    name: str
    on_class: bool


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ExceptionInformation( InformationBase ): pass


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ReturnInformation( InformationBase ): pass


Informations: __.typx.TypeAlias = __.cabc.Sequence[ InformationBase ]


class Formatter( __.typx.Protocol ):
    ''' Formatter for arguments, attributes, exceptions, and returns. '''

    @staticmethod
    def __call__(
        possessor: _nomina.Decoratable,
        informations: Informations,
        context: Context,
    ) -> str: raise NotImplementedError


class Notifier( __.typx.Protocol ):
    ''' Notification callback for warning or error condition. '''

    @staticmethod
    def __call__(
        level: _nomina.NotificationLevels, message: str
    ) -> None: raise NotImplementedError
