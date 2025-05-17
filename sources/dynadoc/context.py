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


''' Data transfer objects for execution context. '''


from . import __
from . import interfaces as _interfaces
from . import nomina as _nomina


_fragments_name_default = '_dynadoc_fragments_'
_recursion_limit_name_default = '_dynadoc_recursion_limit_'


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' Context for annotation evaluation, etc.... '''

    notifier: _interfaces.Notifier
    fragment_rectifier: _interfaces.FragmentRectifier
    visibility_predicate: _interfaces.VisibilityPredicate
    fragments_name: str = _fragments_name_default
    recursion_limit_name: str = _recursion_limit_name_default
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
            fragment_rectifier = self.fragment_rectifier,
            visibility_predicate = self.visibility_predicate,
            fragments_name = self.fragments_name,
            recursion_limit_name = self.recursion_limit_name,
            invoker_globals = iglobals,
            resolver_globals = self.resolver_globals,
            resolver_locals = self.resolver_locals )


class RecursionLimiter( __.typx.Protocol ):
    ''' Can return modified recursion control for attribute. '''

    @staticmethod
    def __call__(
        objct: object, recursion: 'RecursionControl'
    ) -> 'RecursionControl': raise NotImplementedError

RecursionLimiters: __.typx.TypeAlias = __.cabc.Sequence[ RecursionLimiter ]


class RecursionTargets( __.enum.IntFlag ):
    ''' Kinds of objects to recursively document. '''

    Null        = 0
    Class       = __.enum.auto( )
    Descriptor  = __.enum.auto( )
    Function    = __.enum.auto( )
    Module      = __.enum.auto( )


RecursionTargetsSansModule = (
        RecursionTargets.Class
    |   RecursionTargets.Descriptor
    |   RecursionTargets.Function )
RecursionTargetsOmni = (
    RecursionTargetsSansModule | RecursionTargets.Module )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class RecursionLimit:
    ''' Limitations on recursive descent. '''

    avoid_inheritance: bool = False
    targets_exclusions: RecursionTargets = RecursionTargets.Null


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class RecursionControl:
    ''' Controls for recursive descent. '''

    inheritance: bool = False
    limiters: RecursionLimiters = ( )
    targets: RecursionTargets = RecursionTargets.Null
    # TODO? Maximum depth.
    #       (Suggested by multiple LLMs; not convinced that it is needed.)

    def evaluate_limits_for( self, objct: object ) -> 'RecursionControl':
        recursion_ = self
        for limiter in self.limiters:
            recursion_ = limiter( objct, recursion_ )
        return recursion_

    def with_limit( self, limit: RecursionLimit ) -> __.typx.Self:
        inheritance = self.inheritance and not limit.avoid_inheritance
        targets = self.targets & ~limit.targets_exclusions
        return type( self )(
            inheritance = inheritance,
            limiters = self.limiters,
            targets = targets )


def avoid_enum_inheritance(
    objct: object, recursion: RecursionControl
) -> RecursionControl:
    ''' Enums inherit copious amounts of documentation. Avoids this. '''
    if isinstance( objct, __.enum.EnumMeta ):
        return recursion.with_limit(
            RecursionLimit( avoid_inheritance = True ) )
    return recursion
