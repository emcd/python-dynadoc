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
    possessor: _nomina.Documentable,
    informations: _interfaces.Informations,
    context: _interfaces.Context,
) -> str:
    return '\n'.join(
        _produce_fragment_partial( possessor, information, context = context )
        for information in informations )


_qualident_regex = __.re.compile( r'''^([\w\.]+).*$''' )
def _extract_qualident( name: str, context: _interfaces.Context ) -> str:
    extract = _qualident_regex.match( name )
    if extract is not None: return extract[ 1 ]
    return '<unknown>'


def _format_annotation(
    annotation: __.typx.Any, context: _interfaces.Context
) -> str:
    if isinstance( annotation, list ):
        seqstr = ', '.join(
            _format_annotation( element, context )
            for element in annotation ) # pyright: ignore[reportUnknownVariableType]
        return f"[ {seqstr} ]"
    origin = __.typx.get_origin( annotation )
    if origin is None:
        return _qualify_object_name( annotation, context )
    arguments = __.typx.get_args( annotation )
    if origin in ( __.types.UnionType, __.typx.Union ):
        return ' | '.join(
            _format_annotation( argument, context ) for argument in arguments )
    oname = _qualify_object_name( origin, context )
    if not arguments: return oname
    if origin is __.typx.Literal:
        argstr = ', '.join( repr( argument ) for argument in arguments )
    else:
        argstr = ', '.join(
            _format_annotation( argument, context ) for argument in arguments )
    return f"{oname}[ {argstr} ]"


def _produce_fragment_partial(
    possessor: _nomina.Documentable,
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
    possessor: _nomina.Documentable,
    information: _interfaces.ArgumentInformation,
    context: _interfaces.Context,
) -> str:
    description = information.description or ''
    typetext = _format_annotation( information.annotation, context )
    lines: list[ str ] = [
        f":argument {information.name}: {description}",
        f":type {information.name}: {typetext}",
    ]
    return '\n'.join( lines )


def _produce_attribute_text(
    possessor: _nomina.Documentable,
    information: _interfaces.AttributeInformation,
    context: _interfaces.Context,
) -> str:
    description = information.description or ''
    typetext = _format_annotation( information.annotation, context )
    vlabel = (
        ( 'cvar' if information.on_class else 'ivar' )
        if __.inspect.isclass( possessor ) else 'var' )
    lines: list[ str ] = [
        f":{vlabel} {information.name}: {description}",
        f":vartype {information.name}: {typetext}",
    ]
    return '\n'.join( lines )


def _produce_exception_text(
    possessor: _nomina.Documentable,
    information: _interfaces.ExceptionInformation,
    context: _interfaces.Context,
) -> str:
    lines: list[ str ] = [ ]
    annotation = information.annotation
    description = information.description or ''
    if isinstance( annotation, ( __.types.UnionType, __.typx.Union ) ):
        annotations = __.typx.get_args( annotation )
    else: annotations = ( annotation, )
    for annotation_ in annotations:
        typetext = _format_annotation( annotation_, context )
        lines.append( f":raises {typetext}: {description}" )
    return '\n'.join( lines )


def _produce_return_text(
    possessor: _nomina.Documentable,
    information: _interfaces.ReturnInformation,
    context: _interfaces.Context,
) -> str:
    if information.annotation in ( None, __.types.NoneType ): return ''
    description = information.description or ''
    typetext = _format_annotation( information.annotation, context )
    lines: list[ str ] = [ ]
    if description:
        lines.append( f":returns: {description}" )
    lines.append( f":rtype: {typetext}" )
    return '\n'.join( lines )


def _qualify_object_name( # noqa: PLR0911
    objct: object, context: _interfaces.Context
) -> str:
    if objct is Ellipsis: return '...'
    if objct is __.types.NoneType: return 'None'
    name = (
        getattr( objct, '__name__', None )
        or _extract_qualident( str( objct ), context ) )
    if name == '<unknown>': return name
    qname = getattr( objct, '__qualname__', None ) or name
    name0 = qname.split( '.', maxsplit = 1 )[ 0 ]
    if name0 in vars( __.builtins ): # int, etc...
        return qname
    if context.invoker_globals and name0 in context.invoker_globals:
        return qname
    mname = getattr( objct, '__module__', None )
    if mname: return f"{mname}.{qname}"
    return name
