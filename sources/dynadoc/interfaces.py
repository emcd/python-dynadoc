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


try: from typing_extensions import Doc # pyright: ignore[reportAssignmentType]
except ImportError:

    @__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
    class Doc:
        ''' Description of argument or attribute.

            Compatible with :pep:`727` ``Doc`` objects.
        '''

        documentation: str


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Raises:
    ''' Class and description of exception which can be raised.

        Should appear in the return annotations for a function.
    '''

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
class AnnotationsCache:
    ''' Lookup table for reduced annotations from original annotations.

        Has special values for absent and incomplete entries.
    '''

    absent: __.typx.ClassVar[ object ] = object( )
    incomplete: __.typx.ClassVar[ object ] = object( )

    entries: dict[ __.typx.Any, __.typx.Any ] = (
        __.dcls.field( default_factory = dict[ __.typx.Any, __.typx.Any ] ) )

    def access( self, original: __.typx.Any ) -> __.typx.Any:
        ''' Accesses entry value, if it exists.

            Returns absence sentinel if entry does not exist.
        '''
        return self.entries.get( original, self.absent )

    def enter(
        self,
        original: __.typx.Any,
        reduction: __.typx.Any = incomplete,
    ) -> __.typx.Any:
        ''' Adds reduced annotation to cache, returning it.

            Cache key is original annotation.
            If reduction is not specified, then an incompletion sentinel is
            added as the value for the entry.
        '''
        self.entries[ original ] = reduction
        return reduction


class AttributeAssociation( __.enum.Enum ):

    Module      = __.enum.auto( )
    Class       = __.enum.auto( )
    Instance    = __.enum.auto( )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' Context for annotation evaluation, etc.... '''

    notifier: Notifier
    visibility_predicate: VisibilityPredicate
    fragments_name: str = '_dynadoc_fragments_'
    invoker_globals: __.typx.Optional[ _nomina.Variables ] = None
    resolver_globals: __.typx.Optional[ _nomina.Variables ] = None
    resolver_locals: __.typx.Optional[ _nomina.Variables ] = None

    def with_invoker_globals( self, level: int = 2 ) -> __.typx.Self:
        ''' Returns new context with invoker globals from stack frame.

            By default, the stack frame is that of the caller of the caller.
        '''
        iglobals = __.inspect.stack( )[ level ].frame.f_globals
        return type( self )(
            notifier = self.notifier,
            visibility_predicate = self.visibility_predicate,
            fragments_name = self.fragments_name,
            invoker_globals = iglobals,
            resolver_globals = self.resolver_globals,
            resolver_locals = self.resolver_locals )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class InformationBase:
    ''' Base for information on various kinds of entities. '''

    annotation: __.typx.Any
    description: __.typx.Optional[ str ]


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ArgumentInformation( InformationBase ):

    name: str
    paramspec: __.inspect.Parameter


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class AttributeInformation( InformationBase ):

    name: str
    association: AttributeAssociation


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ExceptionInformation( InformationBase ): pass


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ReturnInformation( InformationBase ): pass


Informations: __.typx.TypeAlias = __.cabc.Sequence[ InformationBase ]


class Formatter( __.typx.Protocol ):
    ''' Formatter for arguments, attributes, exceptions, and returns. '''

    @staticmethod
    def __call__(
        possessor: _nomina.Documentable,
        informations: Informations,
        context: Context,
    ) -> str: raise NotImplementedError


class Notifier( __.typx.Protocol ):
    ''' Notification callback for warning or error condition. '''

    @staticmethod
    def __call__(
        level: _nomina.NotificationLevels, message: str
    ) -> None: raise NotImplementedError


class RecursionTargets( __.enum.IntFlag ):
    ''' Kinds of objects to recursively document. '''

    Null        = 0
    Class       = __.enum.auto( )
    Function    = __.enum.auto( )
    Module      = __.enum.auto( )

RecursionTargetsSansModule = (
    RecursionTargets.Class | RecursionTargets.Function )
RecursionTargetsOmni = (
    RecursionTargetsSansModule | RecursionTargets.Module )


class VisibilityPredicate( __.typx.Protocol ):
    ''' Callback to determine attribute visibility. '''

    @staticmethod
    def __call__(
        name: str,
        annotation: __.typx.Any,
        description: __.typx.Optional[ str ],
    ) -> bool: raise NotImplementedError
