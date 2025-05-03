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

from . import __
from . import nomina as _nomina


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' Context for annotation evaluation, etc.... '''

    localvars: __.typx.Optional[ _nomina.Variables ] = None
    globalvars: __.typx.Optional[ _nomina.Variables ] = None


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class InformationBase:
    ''' Base for information on various kinds of entities. '''

    typle: _nomina.Typle
    description: str


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
        context: __.typx.Optional[ Context ] = None,
    ) -> str: raise NotImplementedError


class Introspector( __.typx.Protocol ):
    ''' Annotations introspector for classes and other invocables. '''

    @staticmethod
    def __call__(
        possessor: _nomina.Decoratable,
        context: __.typx.Optional[ Context ] = None,
    ) -> Informations: raise NotImplementedError
