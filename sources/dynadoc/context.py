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
_introspection_limit_name_default = '_dynadoc_introspection_limit_'


GlobalsLevelArgument: __.typx.TypeAlias = __.typx.Annotated[
    int,
    _interfaces.Doc(
        ''' Stack frame level from which to obtain globals.

            Default is 2, which is the caller of the caller.
        ''' ),
]


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' '''

    _dynadoc_fragments_: __.typx.ClassVar[
        _interfaces.Fragments ] = ( 'context', )

    notifier: __.typx.Annotated[
        _interfaces.Notifier, _interfaces.Fname( 'notifier' )
    ]
    fragment_rectifier: __.typx.Annotated[
        _interfaces.FragmentRectifier,
        _interfaces.Fname( 'fragment rectifier' ),
    ]
    visibility_decider: _interfaces.VisibilityDecider
    fragments_name: str = _fragments_name_default
    introspection_limit_name: str = _introspection_limit_name_default
    invoker_globals: __.typx.Optional[ _nomina.Variables ] = None
    resolver_globals: __.typx.Optional[ _nomina.Variables ] = None
    resolver_locals: __.typx.Optional[ _nomina.Variables ] = None

    def with_invoker_globals(
        self, level: GlobalsLevelArgument = 2
    ) -> __.typx.Self:
        ''' Returns new context with invoker globals from stack frame. '''
        iglobals = __.inspect.stack( )[ level ].frame.f_globals
        return type( self )(
            notifier = self.notifier,
            fragment_rectifier = self.fragment_rectifier,
            visibility_decider = self.visibility_decider,
            fragments_name = self.fragments_name,
            introspection_limit_name = self.introspection_limit_name,
            invoker_globals = iglobals,
            resolver_globals = self.resolver_globals,
            resolver_locals = self.resolver_locals )


class ClassIntrospector( __.typx.Protocol ):
    ''' Custom introspector for class annotations and attributes. '''

    @staticmethod
    def __call__( # noqa: PLR0913
        objct: type, /,
        context: Context,
        introspection: 'IntrospectionControl',
        annotations: _nomina.Annotations,
        cache: _interfaces.AnnotationsCache,
        table: _nomina.FragmentsTable,
    ) -> __.typx.Optional[ _interfaces.Informations ]:
        raise NotImplementedError

ClassIntrospectors: __.typx.TypeAlias = (
    __.cabc.Sequence[ ClassIntrospector ] )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ClassIntrospectionLimit:
    ''' Limits on class introspection behavior. '''

    avoid_inheritance: bool = False
    ignore_attributes: bool = False


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ClassIntrospectionControl:
    ''' Controls on class introspection behavior. '''

    inheritance: bool = False
    introspectors: ClassIntrospectors = ( )
    scan_attributes: bool = False

    def with_limit( self, limit: ClassIntrospectionLimit ) -> __.typx.Self:
        inheritance = self.inheritance and not limit.avoid_inheritance
        scan_attributes = self.scan_attributes and not limit.ignore_attributes
        return type( self )(
            inheritance = inheritance,
            introspectors = self.introspectors,
            scan_attributes = scan_attributes )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ModuleIntrospectionLimit:
    ''' Limits on module introspection behavior. '''

    ignore_attributes: bool = False


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class ModuleIntrospectionControl:
    ''' Controls on module introspection behavior. '''

    scan_attributes: bool = False

    def with_limit( self, limit: ModuleIntrospectionLimit ) -> __.typx.Self:
        scan_attributes = self.scan_attributes and not limit.ignore_attributes
        return type( self )( scan_attributes = scan_attributes )


class IntrospectionLimiter( __.typx.Protocol ):
    ''' Can return modified introspection control for attribute. '''

    @staticmethod
    def __call__(
        objct: object, introspection: 'IntrospectionControl'
    ) -> 'IntrospectionControl': raise NotImplementedError

IntrospectionLimiters: __.typx.TypeAlias = (
    __.cabc.Sequence[ IntrospectionLimiter ] )


class IntrospectionTargets( __.enum.IntFlag ):
    ''' Kinds of objects to recursively document. '''

    Null        = 0
    Class       = __.enum.auto( )
    Descriptor  = __.enum.auto( )
    Function    = __.enum.auto( )
    Module      = __.enum.auto( )


IntrospectionTargetsSansModule = (
        IntrospectionTargets.Class
    |   IntrospectionTargets.Descriptor
    |   IntrospectionTargets.Function )
IntrospectionTargetsOmni = (
    IntrospectionTargetsSansModule | IntrospectionTargets.Module )


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class IntrospectionLimit:
    ''' Limits on introspection behavior. '''

    class_limit: ClassIntrospectionLimit = ClassIntrospectionLimit( )
    module_limit: ModuleIntrospectionLimit = ModuleIntrospectionLimit( )
    targets_exclusions: IntrospectionTargets = IntrospectionTargets.Null


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class IntrospectionControl:
    ''' Controls on introspection behavior. '''

    enable: bool = True
    class_control: ClassIntrospectionControl = ClassIntrospectionControl( )
    module_control: ModuleIntrospectionControl = ModuleIntrospectionControl( )
    limiters: IntrospectionLimiters = ( )
    targets: IntrospectionTargets = IntrospectionTargets.Null
    # TODO? Maximum depth.
    #       (Suggested by multiple LLMs; not convinced that it is needed.)

    def evaluate_limits_for( self, objct: object ) -> 'IntrospectionControl':
        ''' Determine which introspection limits apply to object. '''
        introspection_ = self
        for limiter in self.limiters:
            introspection_ = limiter( objct, introspection_ )
        return introspection_

    def with_limit( self, limit: IntrospectionLimit ) -> __.typx.Self:
        class_control = self.class_control.with_limit( limit.class_limit )
        module_control = self.module_control.with_limit( limit.module_limit )
        targets = self.targets & ~limit.targets_exclusions
        return type( self )(
            enable = self.enable,
            class_control = class_control,
            module_control = module_control,
            limiters = self.limiters,
            targets = targets )


# def avoid_enum_inheritance(
#     objct: object, recursion: RecursionControl
# ) -> RecursionControl:
#     ''' Enums inherit copious amounts of documentation. Avoids this. '''
#     if isinstance( objct, __.enum.EnumMeta ):
#         return recursion.with_limit(
#             RecursionLimit( avoid_inheritance = True ) )
#     return recursion
