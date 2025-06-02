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


''' Assert correct function of introspection machinery. '''

# ruff: noqa: E712


import inspect
import types

from . import PACKAGE_NAME, cache_import_module


def test_100_introspect_non_documentable( ):
    ''' introspect returns empty sequence for non-documentable objects. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Create minimal context and introspection control
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection_control = context_module.IntrospectionControl( )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Test with various non-documentable objects
    non_documentable_objects = [
        "string",
        42,
        3.14,
        [ ],
        { },
        lambda x: x,  # lambda function (excluded by name)
        object( ),
    ]
    for obj in non_documentable_objects:
        result = introspection_module.introspect(
            obj, context, introspection_control, cache, table
        )
        assert result == ( ), (
            f"Expected empty sequence for {type( obj ).__name__}, "
            f"got {result}" )


def test_101_introspect_function_with_no_annotations( ):
    ''' introspect handles functions with no annotations gracefully. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection_control = context_module.IntrospectionControl( )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a function with no annotations
    def unannotated_function( x, y ):
        ''' Function without any type annotations. '''
        return x + y
    result = introspection_module.introspect(
        unannotated_function, context, introspection_control, cache, table
    )
    # Should return empty sequence since no annotations to process
    assert result == ( )


def test_102_introspect_function_with_signature_error( ):
    ''' introspect handles functions that raise ValueError during signature
        inspection. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Capture error notifications
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error':
            errors_captured.append( message )
    context = context_module.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection_control = context_module.IntrospectionControl( )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a function that will cause signature inspection to fail
    # We'll mock this by creating a function with problematic attributes
    def problematic_function( ):
        pass
    # Add type annotations to make it worth introspecting
    problematic_function.__annotations__ = { 'return': int }
    # Patch the signature method to raise ValueError
    original_signature = inspect.signature
    def mock_signature( func ):
        if func is problematic_function:
            raise ValueError( "Mock signature error" )
        return original_signature( func )
    # Monkey patch for this test
    inspect.signature = mock_signature
    try:
        result = introspection_module.introspect(
            problematic_function, context, introspection_control, cache, table
        )
        # Should return empty sequence due to signature error
        assert result == ( )
        # Should have captured an error message
        assert len( errors_captured ) == 1
        assert "Could not assess signature" in errors_captured[ 0 ]
        assert "Mock signature error" in errors_captured[ 0 ]
    finally:
        # Restore original signature function
        inspect.signature = original_signature


def test_103_introspect_function_empty_parameters( ):
    ''' _introspect_function handles functions with empty parameters. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a function with return annotation but no parameters
    def no_params_function( ) -> int:
        ''' Function with no parameters but return annotation. '''
        return 42
    # Add return annotation
    no_params_function.__annotations__ = { 'return': int }
    result = introspection_module._introspect_function(
        no_params_function, context, cache, table
    )
    # Should return information about the return value only
    assert len( result ) == 1
    assert isinstance( result[ 0 ], interfaces_module.ReturnInformation )
    assert result[ 0 ].annotation is int


def test_104_introspect_function_missing_return_annotation( ):
    ''' _introspect_function handles functions without return annotations. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a function with parameter annotations but no return annotation
    def no_return_function( x: int ) -> None:
        ''' Function with parameters but no return annotation in
            __annotations__. '''
        pass
    # Manually set annotations without 'return' key
    no_return_function.__annotations__ = { 'x': int }
    result = introspection_module._introspect_function(
        no_return_function, context, cache, table
    )
    # Should return information about parameters only, no return info
    assert len( result ) == 1
    assert isinstance( result[ 0 ], interfaces_module.ArgumentInformation )
    assert result[ 0 ].name == 'x'


def test_200_is_attribute_visible_with_module_all( ):
    ''' is_attribute_visible respects module __all__ when present. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    # Create a mock module with __all__ defined
    mock_module = types.ModuleType( 'mock_module' )
    mock_module.__all__ = [ 'public_attr', 'also_public' ]
    # Test attributes in __all__
    assert introspection_module.is_attribute_visible(
        mock_module, 'public_attr', str, None
    ) == True
    assert introspection_module.is_attribute_visible(
        mock_module, 'also_public', int, None
    ) == True
    # Test attributes not in __all__ (should be hidden even if public-looking)
    assert introspection_module.is_attribute_visible(
        mock_module, 'not_in_all', str, None
    ) == False
    assert introspection_module.is_attribute_visible(
        mock_module, 'another_attr', str, "Has description"
    ) == False  # Even with description, not in __all__


def test_201_is_attribute_visible_without_module_all( ):
    ''' is_attribute_visible uses default logic when module has no __all__. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    # Create a mock module without __all__
    mock_module = types.ModuleType( 'mock_module_no_all' )
    # Explicitly ensure no __all__ attribute
    assert not hasattr( mock_module, '__all__' )
    # Test public names with descriptions
    assert introspection_module.is_attribute_visible(
        mock_module, 'public_attr', str, "Has description"
    ) == True
    # Test public names without descriptions (still visible due to public name)
    assert introspection_module.is_attribute_visible(
        mock_module, 'public_attr', str, None
    ) == True
    # Test private names with descriptions (visible due to description)
    assert introspection_module.is_attribute_visible(
        mock_module, '_private_attr', str, "Has description"
    ) == True
    # Test private names without descriptions (hidden)
    assert introspection_module.is_attribute_visible(
        mock_module, '_private_attr', str, None
    ) == False


def test_300_reduce_annotation_cycle_detection( ):
    ''' reduce_annotation detects and breaks circular references. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Create context with warning capture
    warnings_captured = [ ]
    def capture_notifier( level, message ):
        warnings_captured.append( ( level, message ) )
    context = context_module.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    adjuncts = interfaces_module.AdjunctsData( )
    cache = interfaces_module.AnnotationsCache( )
    # Create a circular reference by manually manipulating the cache
    # This simulates what would happen with truly circular type annotations
    circular_annotation = "SelfReferential"
    # First, mark it as incomplete (this is what happens during processing)
    cache.enter( circular_annotation )  # Marks as incomplete
    # Now try to reduce it again - this should detect the cycle
    result = introspection_module.reduce_annotation(
        circular_annotation, context, adjuncts, cache
    )
    # Should return Any and issue a warning
    typing_module = cache_import_module( f"{PACKAGE_NAME}.__" )
    assert result is typing_module.typx.Any
    # Should have captured a cycle detection warning
    assert len( warnings_captured ) == 1
    level, message = warnings_captured[ 0 ]
    assert level == 'admonition'
    assert 'circular reference' in message.lower( )
    assert 'SelfReferential' in message


def test_301_reduce_annotation_normal_caching( ):
    ''' reduce_annotation caches results normally for non-circular cases. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    adjuncts = interfaces_module.AdjunctsData( )
    cache = interfaces_module.AnnotationsCache( )
    # Test with a simple annotation
    simple_annotation = int
    # First reduction
    result1 = introspection_module.reduce_annotation(
        simple_annotation, context, adjuncts, cache
    )
    # Second reduction should hit cache
    result2 = introspection_module.reduce_annotation(
        simple_annotation, context, adjuncts, cache
    )
    # Results should be identical and cached
    assert result1 is result2
    assert result1 is int
    # Verify it's actually in the cache
    cached_result = cache.access( simple_annotation )
    assert cached_result is int


def test_500_access_annotations_exception_handler( ):
    ''' _access_annotations handles TypeError gracefully. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    # Capture error notifications
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error':
            errors_captured.append( message )
    context = context_module.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create an object that will cause get_annotations to fail
    problematic_object = types.ModuleType( 'test_module' )
    # Patch get_annotations to raise TypeError
    original_get_annotations = inspect.get_annotations
    def mock_get_annotations( obj, **kwargs ):
        if obj is problematic_object:
            raise TypeError( "Mock annotation access error" )
        return original_get_annotations( obj, **kwargs )
    inspect.get_annotations = mock_get_annotations
    try:
        # This should be a private function, so we need to access it
        result = introspection_module._access_annotations(
            problematic_object, context
        )
        # Should return empty mapping due to exception
        assert len( result ) == 0
        # Should have captured an error message
        assert len( errors_captured ) == 1
        assert "Cannot access annotations" in errors_captured[ 0 ]
        assert "Mock annotation access error" in errors_captured[ 0 ]
    finally:
        # Restore original function
        inspect.get_annotations = original_get_annotations


def test_501_filter_reconstitute_annotation_exception_handler( ):
    ''' _filter_reconstitute_annotation handles TypeError gracefully. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Capture error notifications
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error':
            errors_captured.append( message )
    context = context_module.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    adjuncts = interfaces_module.AdjunctsData( )
    cache = interfaces_module.AnnotationsCache( )
    # Create a mock origin that will fail reconstruction

    class ProblematicOrigin:
        __name__ = "ProblematicType"
        def __getitem__( self, args ):
            raise TypeError( "Cannot reconstruct with these arguments" )

    origin = ProblematicOrigin( )
    # Arguments that will cause reconstruction to fail
    arguments = ( int, str )
    # Call the private function
    result = introspection_module._filter_reconstitute_annotation(
        origin, arguments, context, adjuncts, cache
    )
    # Should return the original origin due to exception
    assert result is origin
    # Should have captured an error message
    assert len( errors_captured ) == 1
    assert "Cannot reconstruct" in errors_captured[ 0 ]
    assert "ProblematicType" in errors_captured[ 0 ]


def test_502_reduce_annotation_core_no_arguments( ):
    ''' _reduce_annotation_core handles types with no arguments. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    adjuncts = interfaces_module.AdjunctsData( )
    cache = interfaces_module.AnnotationsCache( )
    # Create a mock generic type with no arguments

    class MockGeneric:
        pass

    # Mock get_origin and get_args to simulate a generic with no arguments
    typing_module = cache_import_module( f"{PACKAGE_NAME}.__" )
    original_get_origin = typing_module.typx.get_origin
    original_get_args = typing_module.typx.get_args
    def mock_get_origin( annotation ):
        if annotation is MockGeneric:
            return object  # Some non-None origin
        return original_get_origin( annotation )
    def mock_get_args( annotation ):
        if annotation is MockGeneric:
            return ( )  # Empty arguments tuple
        return original_get_args( annotation )
    typing_module.typx.get_origin = mock_get_origin
    typing_module.typx.get_args = mock_get_args
    try:
        result = introspection_module._reduce_annotation_core(
            MockGeneric, context, adjuncts, cache
        )
        # Should return the annotation unchanged when no arguments
        assert result is MockGeneric
    finally:
        # Restore original functions
        typing_module.typx.get_origin = original_get_origin
        typing_module.typx.get_args = original_get_args


def test_503_introspect_module_scan_attributes( ):
    ''' _introspect_module scans unannotated module attributes when
        enabled. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Use realistic visibility decider (same as default behavior)
    def realistic_visibility_decider(
        possessor, name, annotation, description
    ):
        return bool( description ) or not name.startswith( '_' )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = realistic_visibility_decider
    )
    # Create introspection control with scan_attributes enabled
    introspection_control = context_module.IntrospectionControl(
        module_control = context_module.ModuleIntrospectionControl(
            scan_attributes = True
        )
    )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a mock module with mixed attributes
    mock_module = types.ModuleType( 'test_scan_module' )
    mock_module.annotated_attr = "annotated"
    mock_module.unannotated_attr = "unannotated"
    mock_module._private_attr = "private"
    mock_module.some_function = lambda: None
    # Add annotations to the module (only annotated_attr)
    mock_module.__annotations__ = { 'annotated_attr': str }
    # Call _introspect_module with scan_attributes enabled
    result = introspection_module._introspect_module(
        mock_module, context, introspection_control, cache, table
    )
    # Should find both annotated and unannotated attributes
    found_names = [ info.name for info in result ]
    assert 'annotated_attr' in found_names      # From annotations
    assert 'unannotated_attr' in found_names    # From scan_attributes
    assert '_private_attr' not in found_names   # Private, no description
    assert 'some_function' not in found_names   # Callable
    # Should not find built-in module attributes
    builtin_attrs = [
        '__doc__', '__loader__', '__name__', '__package__', '__spec__'
    ]
    for attr in builtin_attrs:
        assert attr not in found_names
    # Check both types of attributes found
    annotated_info = next(
        info for info in result if info.name == 'annotated_attr'
    )
    assert annotated_info.annotation is str
    unannotated_info = next(
        info for info in result if info.name == 'unannotated_attr'
    )
    assert unannotated_info.annotation is interfaces_module.absent
    assert unannotated_info.description is None


def test_504_introspect_class_scan_attributes( ):
    ''' _introspect_class scans unannotated class attributes when enabled. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Use realistic visibility decider
    def realistic_visibility_decider(
        possessor, name, annotation, description
    ):
        return bool( description ) or not name.startswith( '_' )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = realistic_visibility_decider
    )
    # Create introspection control with scan_attributes enabled
    introspection_control = context_module.IntrospectionControl(
        class_control = context_module.ClassIntrospectionControl(
            scan_attributes = True
        )
    )
    cache = interfaces_module.AnnotationsCache( )
    table = { }
    # Create a mock class with mixed attributes

    class MockClass:
        # This will be in __annotations__ and should be skipped in scan
        annotated_attr: str = "annotated"
        # This should be found by scan
        unannotated_attr = "unannotated"
        # This is callable and should be skipped by scan
        def some_method( self ):
            pass
        # This is private and should be filtered out
        _private_attr = "private"

    # Add annotations
    MockClass.__annotations__ = { 'annotated_attr': str }
    MockClass.__module__ = 'test_module'
    MockClass.__qualname__ = 'MockClass'
    # Call _introspect_class with scan_attributes enabled
    result = introspection_module._introspect_class(
        MockClass, context, introspection_control, cache, table
    )
    # Should find both annotated and unannotated attributes, but not callables
    found_names = [ info.name for info in result ]
    assert 'annotated_attr' in found_names      # From annotations
    assert 'unannotated_attr' in found_names    # From scan_attributes
    # Callable, documented separately
    assert 'some_method' not in found_names
    assert '_private_attr' not in found_names   # Private, no description
    # Check both types of attributes found
    annotated_info = next(
        info for info in result if info.name == 'annotated_attr'
    )
    assert annotated_info.annotation is str
    unannotated_info = next(
        info for info in result if info.name == 'unannotated_attr'
    )
    assert unannotated_info.annotation is interfaces_module.absent
    assert unannotated_info.description is None


def test_600_is_attribute_visible_conceal( ):
    ''' _is_attribute_visible respects Visibilities.Conceal annotation. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Create context with visibility decider that would normally show attribute
    def permissive_visibility_decider(
        possessor, name, annotation, description
    ):
        return True  # Would normally show everything
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = permissive_visibility_decider
    )
    # Create adjuncts with Conceal visibility
    adjuncts = interfaces_module.AdjunctsData( )
    adjuncts.extras.append( interfaces_module.Visibilities.Conceal )
    # Test with a mock possessor
    mock_possessor = types.ModuleType( 'mock_module' )
    # Should return False despite permissive visibility decider
    result = introspection_module._is_attribute_visible(
        mock_possessor, 'test_attr', str, context, adjuncts, 'Has description'
    )
    assert result == False


def test_601_is_attribute_visible_reveal( ):
    ''' _is_attribute_visible respects Visibilities.Reveal annotation. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Create context with visibility decider that would normally hide attribute
    def restrictive_visibility_decider(
        possessor, name, annotation, description
    ):
        return False  # Would normally hide everything
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = restrictive_visibility_decider
    )
    # Create adjuncts with Reveal visibility
    adjuncts = interfaces_module.AdjunctsData( )
    adjuncts.extras.append( interfaces_module.Visibilities.Reveal )
    # Test with a mock possessor
    mock_possessor = types.ModuleType( 'mock_module' )
    # Should return True despite restrictive visibility decider
    result = introspection_module._is_attribute_visible(
        mock_possessor, '_hidden_attr', str, context, adjuncts, None
    )
    assert result == True


def test_602_is_attribute_visible_default_fallback( ):
    ''' _is_attribute_visible falls back to context visibility decider for
        Default visibility. '''
    introspection_module = cache_import_module(
        f"{PACKAGE_NAME}.introspection" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    # Track visibility decider calls
    visibility_calls = [ ]
    def tracking_visibility_decider(
        possessor, name, annotation, description
    ):
        visibility_calls.append( ( possessor, name, annotation, description ) )
        return name.startswith( 'visible' )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = tracking_visibility_decider
    )
    # Create adjuncts with Default visibility (or no visibility at all)
    adjuncts = interfaces_module.AdjunctsData( )
    adjuncts.extras.append( interfaces_module.Visibilities.Default )
    # Test with a mock possessor
    mock_possessor = types.ModuleType( 'mock_module' )
    # Test visible attribute
    result1 = introspection_module._is_attribute_visible(
        mock_possessor, 'visible_attr', int, context, adjuncts, 'Description'
    )
    assert result1 == True
    # Test hidden attribute
    result2 = introspection_module._is_attribute_visible(
        mock_possessor, 'hidden_attr', str, context, adjuncts, None
    )
    assert result2 == False
    # Should have called visibility decider twice
    assert len( visibility_calls ) == 2
    # Verify calls had correct parameters
    call1 = visibility_calls[ 0 ]
    assert call1[ 0 ] is mock_possessor
    assert call1[ 1 ] == 'visible_attr'
    assert call1[ 2 ] is int
    assert call1[ 3 ] == 'Description'
    call2 = visibility_calls[ 1 ]
    assert call2[ 0 ] is mock_possessor
    assert call2[ 1 ] == 'hidden_attr'
    assert call2[ 2 ] is str
    assert call2[ 3 ] is None
