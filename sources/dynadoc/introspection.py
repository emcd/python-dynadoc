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


''' Introspection of argument, attribute, and return annotations. '''


from __future__ import annotations

from . import __
from . import interfaces as _interfaces
from . import nomina as _nomina


def introspect(
    possessor: _nomina.Decoratable,
    context: __.typx.Optional[ _interfaces.Context ] = None,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    if __.inspect.isclass( possessor ):
        return _introspect_class( possessor, context = context )
    if __.inspect.isfunction( possessor ) and possessor.__name__ != '<lambda>':
        return _introspect_function( possessor, context = context )
    # TODO? Other descriptors, like properties.
    return ( )


def _introspect_class(
    possessor: _nomina.Decoratable,
    context: __.typx.Optional[ _interfaces.Context ] = None,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context = context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    for annotation in annotations:
        # TODO: Introspect attribute annotation.
        pass
    return tuple( informations )


def _introspect_function(
    possessor: _nomina.Decoratable,
    context: __.typx.Optional[ _interfaces.Context ] = None,
) -> __.cabc.Sequence[ _interfaces.InformationBase ]:
    annotations = _access_annotations( possessor, context = context )
    if not annotations: return ( )
    informations: list[ _interfaces.InformationBase ] = [ ]
    # TODO: Implement.
    return tuple( informations )


def _access_annotations(
    possessor: _nomina.Decoratable,
    context: __.typx.Optional[ _interfaces.Context ] = None,
) -> __.cabc.Mapping[ str, __.typx.Any ]:
    nomargs: _nomina.Variables = dict( eval_str = True )
    if context:
        nomargs[ 'locals' ] = context.localvars
        nomargs[ 'globals' ] = context.globalvars
    try:
        return __.types.MappingProxyType(
            __.inspect.get_annotations( possessor, **nomargs ) )
    except TypeError:
        # TODO: Issue warning.
        return __.dictproxy_empty
