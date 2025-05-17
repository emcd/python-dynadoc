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


@__.dcls.dataclass( frozen = True, kw_only = True, slots = True )
class Context:
    ''' Context for annotation evaluation, etc.... '''

    notifier: _interfaces.Notifier
    fragment_rectifier: _interfaces.FragmentRectifier
    visibility_predicate: _interfaces.VisibilityPredicate
    fragments_name: str = _fragments_name_default
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
            invoker_globals = iglobals,
            resolver_globals = self.resolver_globals,
            resolver_locals = self.resolver_locals )
