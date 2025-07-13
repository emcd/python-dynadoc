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


''' Assert correct function of Sphinx autodoc renderer. '''


import types

from . import PACKAGE_NAME, cache_import_module


def test_100_format_annotation_no_arguments( ):
    ''' _format_annotation handles generic types with no arguments. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create a mock generic type with origin but no arguments
    class MockGeneric:
        pass
    # Mock typing functions to simulate a generic with no arguments
    typing_module = cache_import_module( f"{PACKAGE_NAME}.__" )
    original_get_origin = typing_module.typx.get_origin
    original_get_args = typing_module.typx.get_args
    def mock_get_origin( annotation ):
        if annotation is MockGeneric:
            return list  # Some origin
        return original_get_origin( annotation )
    def mock_get_args( annotation ):
        if annotation is MockGeneric:
            return ( )  # No arguments
        return original_get_args( annotation )
    typing_module.typx.get_origin = mock_get_origin
    typing_module.typx.get_args = mock_get_args
    try:
        result = renderers_module._format_annotation(
            MockGeneric, context, renderers_module.Style.Legible
        )
        # Should return just the origin name when no arguments
        assert result == "list"
    finally:
        # Restore original functions
        typing_module.typx.get_origin = original_get_origin
        typing_module.typx.get_args = original_get_args


def test_101_format_annotation_forward_ref( ):
    ''' _format_annotation handles ForwardRef objects. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    typing_module = cache_import_module( f"{PACKAGE_NAME}.__" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    forward_ref = typing_module.typx.ForwardRef( 'SomeType' )
    result = renderers_module._format_annotation(
        forward_ref, context, renderers_module.Style.Legible
    )
    assert result == 'SomeType'


def test_102_produce_fragment_partial_unrecognized_information( ):
    ''' _produce_fragment_partial handles unrecognized information types. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    # Capture notifications
    notifications = [ ]
    def capture_notifier( level, message ):
        notifications.append( ( level, message ) )
    context = context_module.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create an unrecognized information type
    class UnrecognizedInformation:
        pass
    unrecognized = UnrecognizedInformation( )
    # Create a mock possessor
    mock_possessor = types.ModuleType( 'test_module' )
    result = renderers_module._produce_fragment_partial(
        mock_possessor, unrecognized, context, renderers_module.Style.Legible
    )
    # Should return empty string
    assert result == ''
    # Should have issued an admonition
    assert len( notifications ) == 1
    level, message = notifications[ 0 ]
    assert level == 'admonition'
    assert 'Unrecognized information' in message


def test_103_produce_module_attribute_text_surrogate_mode( ):
    ''' _produce_module_attribute_text handles ValuationModes.Surrogate. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create a mock module
    mock_module = types.ModuleType( 'test_module' )
    mock_module.test_attr = "actual_value"
    # Create attribute information with surrogate mode
    info = interfaces_module.AttributeInformation(
        name = 'test_attr',
        annotation = str,
        description = 'Test attribute with surrogate value',
        association = interfaces_module.AttributeAssociations.Module,
        default = interfaces_module.Default(
            mode = interfaces_module.ValuationModes.Surrogate,
            surrogate = 'Custom surrogate description'
        )
    )
    result = renderers_module._produce_module_attribute_text(
        mock_module, info, context, renderers_module.Style.Legible
    )
    # Should not include any value when in surrogate mode
    assert 'py:data:: test_attr' in result
    assert ':type: str' in result
    assert ':value:' not in result
    assert 'actual_value' not in result
    assert 'Custom surrogate description' not in result


def test_104_produce_module_attribute_text_no_annotation( ):
    ''' Handles module attributes without annotations. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create a mock module
    mock_module = types.ModuleType( 'test_module' )
    mock_module.untyped_attr = 42
    # Create attribute information without annotation
    info = interfaces_module.AttributeInformation(
        name = 'untyped_attr',
        annotation = interfaces_module.absent,
        description = 'Attribute without type annotation',
        association = interfaces_module.AttributeAssociations.Module,
        default = interfaces_module.Default( )
    )
    result = renderers_module._produce_module_attribute_text(
        mock_module, info, context, renderers_module.Style.Legible
    )
    # Should not include type information
    assert 'py:data:: untyped_attr' in result
    assert ':type:' not in result
    assert ':value: 42' in result


def test_200_qualify_object_name_unknown_case( ):
    ''' _qualify_object_name handles objects with unknown names. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create an object that will result in <unknown> name
    class NoNameObject:
        def __str__( self ):
            return "!@#$%^&*()"  # No word characters at start
    obj = NoNameObject( )
    result = renderers_module._qualify_object_name( obj, context )
    assert result == '<unknown>'


def test_201_qualify_object_name_invoker_globals( ):
    ''' _qualify_object_name uses invoker_globals when available. '''
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    # Create a mock object with a name
    class TestClass:
        __name__ = 'TestClass'
        __qualname__ = 'TestClass'
    test_obj = TestClass( )
    # Create context with invoker_globals containing the object
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ),
        invoker_globals = { 'TestClass': test_obj }
    )
    result = renderers_module._qualify_object_name( test_obj, context )
    # Should return just the qualname since it's in invoker_globals
    assert result == 'TestClass'
