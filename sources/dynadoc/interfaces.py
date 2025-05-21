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


from . import __
from . import nomina as _nomina


try: from typing_extensions import Doc # pyright: ignore[reportAssignmentType]
except ImportError:

    @__.dcls.dataclass( frozen = True, slots = True )
    class Doc:
        ''' Description of argument or attribute.

            Compatible with :pep:`727` ``Doc`` objects.
        '''

        documentation: str


Fragment: __.typx.TypeAlias = str | Doc
Fragments: __.typx.TypeAlias = __.cabc.Sequence[ Fragment ]


@__.dcls.dataclass( frozen = True, slots = True )
class Fname:
    ''' Name of documentation fragment in table. '''

    name: str


@__.dcls.dataclass( frozen = True, slots = True )
class Raises:
    ''' Class and description of exception which can be raised.

        Should appear in the return annotations for a function.
    '''

    classes: type[ BaseException ] | __.cabc.Sequence[ type[ BaseException ] ]
    description: __.typx.Optional[ str ] = None


class Sentinels( __.enum.Enum ):
    ''' Sentinel values used in various parts of the package. '''

    Absent      = __.enum.auto( )
    Incomplete  = __.enum.auto( )


absent: __.typx.Annotated[
    Sentinels, Doc( ''' Indicates annotation or other data is missing. ''' )
] = Sentinels.Absent
incomplete: __.typx.Annotated[
    Sentinels, Doc( ''' Indicates annotation reduction is incomplete. ''' ),
] = Sentinels.Incomplete


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

    entries: dict[ __.typx.Any, __.typx.Any ] = (
        __.dcls.field( default_factory = dict[ __.typx.Any, __.typx.Any ] ) )

    def access( self, original: __.typx.Any ) -> __.typx.Any:
        ''' Accesses entry value, if it exists.

            Returns absence sentinel if entry does not exist.
        '''
        return self.entries.get( original, absent )

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


class AttributeAssociations( __.enum.Enum ):

    Module      = __.enum.auto( )
    Class       = __.enum.auto( )
    Instance    = __.enum.auto( )


class ValuationModes( __.enum.Enum ):
    ''' Annotation for how default value is determined.

        Accept means to use assigned value.
        Suppress means to use no value.
        Surrogate means to use surrogate value.
    '''

    Accept      = __.enum.auto( )
    Suppress    = __.enum.auto( )
    Surrogate   = __.enum.auto( )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Default:
    ''' How to process default value. '''

    mode: ValuationModes = ValuationModes.Accept
    surrogate: __.typx.Any = absent


class FragmentRectifier( __.typx.Protocol ):
    ''' Callback to clean documentation fragment.

        Example: inspect.cleandoc
    '''

    @staticmethod
    def __call__( fragment: str ) -> str: raise NotImplementedError


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class InformationBase:
    ''' Base for information on various kinds of entities. '''

    annotation: __.typx.Any
    description: __.typx.Optional[ str ]


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ArgumentInformation( InformationBase ):

    name: str
    paramspec: __.inspect.Parameter
    default: Default


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class AttributeInformation( InformationBase ):

    name: str
    association: AttributeAssociations
    default: Default


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ExceptionInformation( InformationBase ): pass


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ReturnInformation( InformationBase ): pass


Informations: __.typx.TypeAlias = __.cabc.Sequence[ InformationBase ]


class Notifier( __.typx.Protocol ):
    ''' Notifies of warnings and errors. '''

    @staticmethod
    def __call__(
        level: _nomina.NotificationLevels, message: str
    ) -> None:
        ''' (Signature for notifier callback.) '''
        raise NotImplementedError


class Visibilities( __.enum.Enum ):
    ''' Annotation to determine visibility of attribute.

        Default means to defer to visibility predicate in use.
        Conceal means to hide regardless of visibility predicate.
        Reveal means to show regardless of visibility predicate.
    '''

    Default     = __.enum.auto( )
    Conceal     = __.enum.auto( )
    Reveal      = __.enum.auto( )


class VisibilityDecider( __.typx.Protocol ):
    ''' Callback to determine attribute visibility. '''

    @staticmethod
    def __call__(
        name: str,
        annotation: __.typx.Any,
        description: __.typx.Optional[ str ],
    ) -> bool: raise NotImplementedError
