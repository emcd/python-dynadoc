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


''' Docstring generation with configurable formats and PEP 727 support. '''


from . import __
from . import context
from . import formatters
from . import introspection
from . import nomina
from . import notification
# --- BEGIN: Injected by Copier ---
# --- END: Injected by Copier ---

# TODO: Collect public interfaces into API module and wildcard export that.
from .assembly import *
from .interfaces import *


__version__: __.typx.Annotated[ str, Visibilities.Reveal ]
__version__ = '1.0a0'


_context = assembly.produce_context(
    notifier = notification.notify_internal )
_introspection_cc = context.ClassIntrospectionControl(
    inheritance = True,
    introspectors = ( introspection.introspect_special_classes, ) )
_introspection = context.IntrospectionControl(
    class_control = _introspection_cc,
    targets = context.IntrospectionTargetsOmni )
assembly.assign_module_docstring(
    __.package_name, context = _context, introspection = _introspection )
# TODO: Reclassify package modules as immutable and concealed.
