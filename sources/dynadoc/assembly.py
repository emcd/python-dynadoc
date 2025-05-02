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


''' Docstring assembly. '''


from __future__ import annotations

from . import __
from . import formatters as _formatters
from . import nomina as _nomina


def with_docstring(
    *fragments: _nomina.WithDocstringFragmentsArgument,
    # TODO? custom context dictionary (default: module vars of decoratable)
    formatter: _nomina.WithDocstringFormatterArgument = (
        _formatters.format_sphinx_rst ),
    # TODO? custom introspecter
    preserve: _nomina.WithDocstringPreserveArgument = True,
    table: _nomina.WithDocstringTableArgument = __.dictproxy_empty,
) -> _nomina.Decorator:
    ''' Assembles docstring from fragments and decorates object with it. '''
    def decorate( obj: _nomina.Decoratable ) -> _nomina.Decoratable:
        fragments_: list[ str ] = [ ]
        if preserve:
            fragment = __.inspect.getdoc( obj )
            if fragment: fragments_.append( fragment )
        fragments_.extend(
            (   fragment.documentation
                if isinstance( fragment, __.typx.Doc )
                else table[ fragment ] )
            for fragment in fragments )
        # TODO: Introspect and format.
        docstring = '\n\n'.join(
            __.inspect.cleandoc( fragment ) for fragment in fragments_ )
        obj.__doc__ = docstring if docstring else None
        return obj

    return decorate
