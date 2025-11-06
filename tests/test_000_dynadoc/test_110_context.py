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


''' Assert correct function of context DTOs. '''


import warnings

from .__ import PACKAGE_NAME, cache_import_module

# import pytest


MODULE_QNAME = f"{PACKAGE_NAME}.context"


def _is_attribute_visible( possessor, name, annotation, description ):
    return True

def _notify( level, message ):
    warnings.warn( message, category = RuntimeWarning, stacklevel = 2 )

def _rectify_fragment( fragment, source ): return source


def test_020_context_with_invoker_globals( ):
    ''' Derived context has globals from correct stack frame. '''
    module = cache_import_module( MODULE_QNAME )
    context = module.Context(
        notifier = _notify,
        fragment_rectifier = _rectify_fragment,
        visibility_decider = _is_attribute_visible )
    context_ig = context.with_invoker_globals( level = 1 )
    assert 'PACKAGE_NAME' in context_ig.invoker_globals
    assert PACKAGE_NAME == context_ig.invoker_globals[ 'PACKAGE_NAME' ]
