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


''' Assert correct function of internal machinery. '''


import warnings

import pytest

from .__ import PACKAGE_NAME, cache_import_module


@pytest.mark.parametrize( 'level', ( 'admonition', 'error' ) )
def test_100_notifier( level ):
    ''' Internal notifier emits warnings. '''
    module = cache_import_module( f"{PACKAGE_NAME}" )
    notifier = module._notify
    with warnings.catch_warnings( record = True ) as warns:
        notifier( level, "foobar" )
        assert issubclass( warns[ -1 ].category, RuntimeWarning )
        assert "foobar" in str( warns[ -1 ].message )
