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


''' Eating our own dog food. Practicing our doc fu. Package is doc fu'd.

    Ordinarily, the ``with_docstring`` decorator would be applied via the
    decorator syntax. However, since it is defined within this package, this
    would lead to dependency cycles if we tried to do it on elements of the
    package API. Therefore, we apply the decorator using function syntax after
    everything has been defined in the fully-imported package modules.
'''


from __future__ import annotations

from . import __
from . import assembly as _assembly
from . import formatters as _formatters
from . import interfaces as _interfaces
from . import introspection as _introspection
from . import notification as _notification


context = _assembly.produce_context(
    notifier = _notification.notify_internal )
with_docstring = __.funct.partial(
    _assembly.with_docstring, context = context, recurse = True )


with_docstring( )( _assembly.produce_context )
with_docstring( )( _assembly.with_docstring )

with_docstring( )( _interfaces.Raises )
with_docstring( )( _interfaces.AdjunctsData )
with_docstring( )( _interfaces.AnnotationsCache )
with_docstring( )( _interfaces.Context )
with_docstring( )( _interfaces.InformationBase )
with_docstring( )( _interfaces.ArgumentInformation )
with_docstring( )( _interfaces.AttributeInformation )
with_docstring( )( _interfaces.ExceptionInformation )
with_docstring( )( _interfaces.ReturnInformation )
with_docstring( )( _interfaces.Formatter )
with_docstring( )( _interfaces.Notifier )
with_docstring( )( _interfaces.VisibilityPredicate )

with_docstring( )( _introspection.introspect )
with_docstring( )( _introspection.is_attribute_visible )

with_docstring( )( _formatters.sphinxrst.produce_fragment )
