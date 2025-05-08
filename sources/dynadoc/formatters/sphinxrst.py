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


''' Sphinx reStructuredText formatters. '''


from __future__ import annotations

from .. import interfaces as _interfaces
from .. import nomina as _nomina
from . import __


def produce_fragment(
    possessor: _nomina.Decoratable,
    informations: _interfaces.Informations,
    context: _interfaces.Context,
) -> str:
    return '\n'.join(
        _produce_fragment_partial( possessor, information, context = context )
        for information in informations )


def _format_annotation(
    annotation: __.typx.Any, context: _interfaces.Context
) -> str:
    return 'Exception'


def _produce_fragment_partial(
    possessor: _nomina.Decoratable,
    information: _interfaces.InformationBase,
    context: _interfaces.Context,
) -> str:
    if isinstance( information, _interfaces.ArgumentInformation ):
        return (
            _produce_argument_text(
                possessor, information, context = context ) )
    if isinstance( information, _interfaces.AttributeInformation ):
        return (
            _produce_attribute_text(
                possessor, information, context = context ) )
    if isinstance( information, _interfaces.ExceptionInformation ):
        return (
            _produce_exception_text(
                possessor, information, context = context ) )
    if isinstance( information, _interfaces.ReturnInformation ):
        return (
            _produce_return_text(
                possessor, information, context = context ) )
    context.notifier(
        'admonition', f"Unrecognized information: {information!r}" )
    return ''


def _produce_argument_text(
    possessor: _nomina.Decoratable,
    information: _interfaces.ArgumentInformation,
    context: _interfaces.Context,
) -> str:
    typetext = _format_annotation( information.annotation, context )
    lines: list[ str ] = [ ]
    if information.description:
        lines.append(
            f":argument {information.name}: {information.description}" )
    lines.append( f":type {information.name}: {typetext}" )
    return '\n'.join( lines )


def _produce_attribute_text(
    possessor: _nomina.Decoratable,
    information: _interfaces.AttributeInformation,
    context: _interfaces.Context,
) -> str:
    typetext = _format_annotation( information.annotation, context )
    vlabel = 'cvar' if information.on_class else 'ivar'
    lines: list[ str ] = [ ]
    if information.description:
        lines.append(
            f":{vlabel} {information.name}: {information.description}" )
    lines.append( f":vartype {information.name}: {typetext}" )
    return '\n'.join( lines )


def _produce_exception_text(
    possessor: _nomina.Decoratable,
    information: _interfaces.ExceptionInformation,
    context: _interfaces.Context,
) -> str:
    # TODO? Iterate over compound annotation and emit separate lines.
    typetext = _format_annotation( information.annotation, context )
    lines: list[ str ] = [ ]
    lines.append( f":raises {typetext}: {information.description}" )
    return '\n'.join( lines )


def _produce_return_text(
    possessor: _nomina.Decoratable,
    information: _interfaces.ReturnInformation,
    context: _interfaces.Context,
) -> str:
    typetext = _format_annotation( information.annotation, context )
    lines: list[ str ] = [ ]
    if information.description:
        lines.append( f":returns: {information.description}" )
    lines.append( f":rtype: {typetext}" )
    return '\n'.join( lines )
