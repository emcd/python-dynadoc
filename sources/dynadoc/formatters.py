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


''' Formatters for introspected arguments, attributes, and returns. '''
# TODO: split into subpackage, one module per output format
# TODO: argument species: posonly, positional, nomonly, nominative
# TODO: attribute species: class, instance
# TODO: annotation as sequence of classes or special typeform (Any, etc...)
#       also "indexed classes" (e.g., set[ str ])
# TODO: genus: exception (from special dynadoc.Exception annotations)


from __future__ import annotations

from . import __
from . import nomina as _nomina


def format_sphinx_rst(
    name: str, genus: _nomina.SubjectGenus, annotation: __.typx.Any
) -> str:
    ''' Derives Sphinx reStructuredText for subject. '''
    match genus:
        case 'argument':
            return _format_sphinx_rst_argument( name, annotation )
        case 'attribute':
            return _format_sphinx_rst_attribute( name, annotation )
        case 'return':
            return _format_sphinx_rst_return( name, annotation )


def _format_sphinx_rst_argument( name: str, annotation: __.typx.Any ) -> str:
    # TODO: Implement.
    return ''


def _format_sphinx_rst_attribute( name: str, annotation: __.typx.Any ) -> str:
    # TODO: Implement.
    return ''


def _format_sphinx_rst_return( name: str, annotation: __.typx.Any ) -> str:
    # TODO: Implement.
    return ''
