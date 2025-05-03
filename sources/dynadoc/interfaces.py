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


class Formatter( __.typx.Protocol ):
    ''' Formatter for arguments, attributes, exceptions, and returns. '''

    def format_argument( # noqa: PLR0913
        self,
        possessor: _nomina.Decoratable,
        context: _nomina.Modulevars,
        name: str,
        paramspec: __.inspect.Parameter,
        typle: _nomina.Typle,
        description: str,
    ) -> str:
        ''' Renders argument in target format. '''
        raise NotImplementedError

    def format_attribute( # noqa: PLR0913
        self,
        possessor: _nomina.Decoratable,
        context: _nomina.Modulevars,
        name: str,
        species: _nomina.AttributeSpecies,
        typle: _nomina.Typle,
        description: str,
    ) -> str:
        ''' Renders attribute in target format. '''
        raise NotImplementedError

    def format_exception(
        self,
        possessor: _nomina.Decoratable,
        context: _nomina.Modulevars,
        name: str,
        typle: _nomina.Typle,
        description: str,
    ) -> str:
        ''' Renders exception in target format. '''
        raise NotImplementedError

    def format_return(
        self,
        possessor: _nomina.Decoratable,
        context: _nomina.Modulevars,
        name: str,
        typle: _nomina.Typle,
        description: str,
    ) -> str:
        ''' Renders return in target format. '''
        raise NotImplementedError
