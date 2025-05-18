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


from .. import context as _context
from .. import interfaces as _interfaces
from .. import introspection as _introspection
from .. import nomina as _nomina
from . import __


class Style( __.enum.Enum ):
    ''' Style of formatter output. '''

    Legible     = __.enum.auto( )
    Pep8        = __.enum.auto( )


def produce_fragment(
    possessor: _nomina.Documentable,
    informations: _interfaces.Informations,
    context: _context.Context,
    style: Style = Style.Legible,
) -> str:
    return '\n'.join(
        _produce_fragment_partial( possessor, information, context, style )
        for information in informations )


_qualident_regex = __.re.compile( r'''^([\w\.]+).*$''' )
def _extract_qualident( name: str, context: _context.Context ) -> str:
    extract = _qualident_regex.match( name )
    if extract is not None: return extract[ 1 ]
    return '<unknown>'


def _format_annotation(
    annotation: __.typx.Any, context: _context.Context, style: Style
) -> str:
    if isinstance( annotation, list ):
        seqstr = ', '.join(
            _format_annotation( element, context, style )
            for element in annotation ) # pyright: ignore[reportUnknownVariableType]
        return _stylize_delimiter( style, '[]', seqstr )
    origin = __.typx.get_origin( annotation )
    if origin is None:
        return _qualify_object_name( annotation, context )
    arguments = __.typx.get_args( annotation )
    if origin in ( __.types.UnionType, __.typx.Union ):
        return ' | '.join(
            _format_annotation( argument, context, style )
            for argument in arguments )
    oname = _qualify_object_name( origin, context )
    if not arguments: return oname
    if origin is __.typx.Literal:
        argstr = ', '.join( repr( argument ) for argument in arguments )
    else:
        argstr = ', '.join(
            _format_annotation( argument, context, style )
            for argument in arguments )
    return _stylize_delimiter( style, '[]', argstr, oname )


def _produce_fragment_partial(
    possessor: _nomina.Documentable,
    information: _interfaces.InformationBase,
    context: _context.Context,
    style: Style,
) -> str:
    if isinstance( information, _interfaces.ArgumentInformation ):
        return (
            _produce_argument_text( possessor, information, context, style ) )
    if isinstance( information, _interfaces.AttributeInformation ):
        return (
            _produce_attribute_text( possessor, information, context, style ) )
    if isinstance( information, _interfaces.ExceptionInformation ):
        return (
            _produce_exception_text( possessor, information, context, style ) )
    if isinstance( information, _interfaces.ReturnInformation ):
        return (
            _produce_return_text( possessor, information, context, style ) )
    context.notifier(
        'admonition', f"Unrecognized information: {information!r}" )
    return ''


def _produce_argument_text(
    possessor: _nomina.Documentable,
    information: _interfaces.ArgumentInformation,
    context: _context.Context,
    style: Style,
) -> str:
    annotation = information.annotation
    description = information.description or ''
    lines: list[ str ] = [ ]
    lines.append( f":argument {information.name}: {description}" )
    if annotation is not _interfaces.absent:
        typetext = _format_annotation( annotation, context, style )
        lines.append( f":type {information.name}: {typetext}" )
    return '\n'.join( lines )


def _produce_attribute_text(
    possessor: _nomina.Documentable,
    information: _interfaces.AttributeInformation,
    context: _context.Context,
    style: Style,
) -> str:
    annotation = information.annotation
    description = information.description or ''
    name = information.name
    match information.association:
        case _interfaces.AttributeAssociations.Module:
            return _produce_module_attribute_text(
                possessor, information, context, style )
        case _interfaces.AttributeAssociations.Class: vlabel = 'cvar'
        case _interfaces.AttributeAssociations.Instance: vlabel = 'ivar'
    lines: list[ str ] = [ ]
    lines.append( f":{vlabel} {name}: {description}" )
    if annotation is not _interfaces.absent:
        typetext = _format_annotation( annotation, context, style )
        lines.append( f":vartype {name}: {typetext}" )
    return '\n'.join( lines )


def _produce_module_attribute_text(
    possessor: _nomina.Documentable,
    information: _interfaces.AttributeInformation,
    context: _context.Context,
    style: Style,
) -> str:
    annotation = information.annotation
    description = information.description or ''
    name = information.name
    value = getattr( possessor, name, _interfaces.absent )
    lines: list[ str ] = [ ]
    if annotation is __.typx.TypeAlias:
        lines.append( f".. py:type:: {name}" )
        value_a = getattr( possessor, name )
        if value is not _interfaces.absent:
            value_ar = _introspection.reduce_annotation(
                value_a, context,
                _interfaces.AdjunctsData( ),
                _interfaces.AnnotationsCache( ) )
            value_s = _format_annotation( value_ar, context, style )
            lines.append( f"   :canonical: {value_s}" )
        lines.extend( [ '', f"   {description}" ] )
    else:
        # Note: No way to inject data docstring as of 2025-05-11.
        #       Autodoc will read doc comments and pseudo-docstrings,
        #       but we have no means of supplying description via a field.
        lines.append( f".. py:data:: {name}" )
        if annotation is not _interfaces.absent:
            typetext = _format_annotation( annotation, context, style )
            lines.append( f"    :type: {typetext}" )
        if value is not _interfaces.absent:
            lines.append( f"    :value: {value!r}" )
    return '\n'.join( lines )


def _produce_exception_text(
    possessor: _nomina.Documentable,
    information: _interfaces.ExceptionInformation,
    context: _context.Context,
    style: Style,
) -> str:
    lines: list[ str ] = [ ]
    annotation = information.annotation
    description = information.description or ''
    if isinstance( annotation, ( __.types.UnionType, __.typx.Union ) ):
        annotations = __.typx.get_args( annotation )
    else: annotations = ( annotation, )
    for annotation_ in annotations:
        typetext = _format_annotation( annotation_, context, style )
        lines.append( f":raises {typetext}: {description}" )
    return '\n'.join( lines )


def _produce_return_text(
    possessor: _nomina.Documentable,
    information: _interfaces.ReturnInformation,
    context: _context.Context,
    style: Style,
) -> str:
    if information.annotation in ( None, __.types.NoneType ): return ''
    description = information.description or ''
    typetext = _format_annotation( information.annotation, context, style )
    lines: list[ str ] = [ ]
    if description:
        lines.append( f":returns: {description}" )
    lines.append( f":rtype: {typetext}" )
    return '\n'.join( lines )


def _qualify_object_name( # noqa: PLR0911
    objct: object, context: _context.Context
) -> str:
    if objct is Ellipsis: return '...'
    if objct is __.types.NoneType: return 'None'
    if objct is __.types.ModuleType: return 'types.ModuleType'
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


def _stylize_delimiter(
    style: Style,
    delimiters: str,
    content: str,
    prefix: str = '',
) -> str:
    ld = delimiters[ 0 ]
    rd = delimiters[ 1 ]
    match style:
        case Style.Legible: return f"{prefix}{ld} {content} {rd}"
        case Style.Pep8: return f"{prefix}{ld}{content}{rd}"
