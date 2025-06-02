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


''' Assert correct function of assembly machinery. '''

# ruff: noqa: E712


import types

from . import PACKAGE_NAME, cache_import_module


def test_100_assign_module_docstring_with_module_object( ):
    ''' assign_module_docstring accepts actual module objects. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    # Create a test module
    test_module = types.ModuleType( 'test_module' )
    test_module.__doc__ = 'Test module'
    # Call with module object instead of string name
    assembly_module.assign_module_docstring( test_module )
    # Should not raise an exception and should process the module
    assert test_module.__doc__ == 'Test module'


def test_101_collect_fragments_invalid_sequence( ):
    ''' _collect_fragments handles invalid fragments sequence gracefully. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
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
    # Create an object with invalid fragments sequence (not a sequence)
    class InvalidFragmentsClass:
        _dynadoc_fragments_ = 42  # Integer is not a sequence
    obj = InvalidFragmentsClass( )
    result = assembly_module._collect_fragments( obj, context, 'test.fqname' )
    # Should return empty tuple and issue error
    assert result == ( )
    assert len( errors_captured ) == 1
    assert 'Invalid fragments sequence' in errors_captured[ 0 ]


def test_102_collect_fragments_invalid_fragment_type( ):
    ''' _collect_fragments handles invalid fragment types in sequence. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
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
    # Create an object with valid sequence but invalid fragment types
    class InvalidFragmentTypesClass:
        _dynadoc_fragments_ = (
            interfaces_module.Doc( "Valid doc fragment" ),
            42,  # Invalid: not a string or Doc
            "valid string fragment",
            [ "invalid", "list" ],  # Invalid: not a string or Doc
        )
    obj = InvalidFragmentTypesClass( )
    result = assembly_module._collect_fragments( obj, context, 'test.fqname' )
    # Should return the sequence but issue errors for invalid types
    assert len( result ) == 4
    assert len( errors_captured ) == 2  # Two invalid fragments
    assert 'Invalid fragment' in errors_captured[ 0 ]
    assert 'Invalid fragment' in errors_captured[ 1 ]


def test_103_consider_class_attribute_module_recursion( ):
    ''' _consider_class_attribute handles module recursion correctly. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    import types
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection = context_module.IntrospectionControl(
        targets = context_module.IntrospectionTargets.Module
    )
    # Create a mock submodule that would trigger recursion
    mock_submodule = types.ModuleType( 'test_module.submodule' )
    pmname = 'test_module'
    pqname = 'TestClass'
    aname = 'submodule_attr'
    result, update_surface = assembly_module._consider_class_attribute(
        mock_submodule, context, introspection, pmname, pqname, aname
    )
    # Should recognize it as a recursive module and return it
    assert result is mock_submodule
    assert update_surface == False


def test_104_decorate_object_already_visited( ):
    ''' _decorate handles objects already in visitees set. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection = context_module.IntrospectionControl( )
    # Create a test class
    class TestClass:
        pass
    # Manually add to visitees to simulate already visited
    assembly_module._visitees.add( TestClass )
    try:
        # This should return immediately without processing
        assembly_module._decorate(
            TestClass,
            context = context,
            introspection = introspection,
            preserve = True,
            renderer = lambda obj, info, ctx: '',
            fragments = ( ),
            table = { }
        )
        # Should not raise an exception and return quickly
        assert True
    finally:
        # Clean up
        assembly_module._visitees.discard( TestClass )


def test_105_decorate_core_introspection_disabled( ):
    ''' _decorate_core handles disabled introspection. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    import inspect
    def proper_fragment_rectifier( fragment, source ):
        ''' Proper fragment rectifier that cleans docstrings. '''
        if source == interfaces_module.FragmentSources.Docstring:
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create introspection control with introspection disabled
    introspection = context_module.IntrospectionControl( enable = False )
    # Create a test function with annotations
    def test_function( x: int ) -> str:
        ''' Test function. '''
        return str( x )
    # This should not generate introspection information
    assembly_module._decorate_core(
        test_function,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, ctx: ':introspected:',
        fragments = ( ),
        table = { }
    )
    # Should preserve original docstring without introspection
    assert test_function.__doc__ == 'Test function.'


def test_106_limit_introspection_invalid_limit( ):
    ''' _limit_introspection handles invalid introspection limit objects. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
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
    introspection = context_module.IntrospectionControl( )
    # Create an object with invalid introspection limit
    class InvalidLimitClass:
        _dynadoc_introspection_limit_ = "not a valid limit object"
    obj = InvalidLimitClass( )
    result = assembly_module._limit_introspection(
        obj, context, introspection, 'test.fqname'
    )
    # Should return original introspection and issue error
    assert result is introspection
    assert len( errors_captured ) == 1
    assert 'Invalid introspection limit' in errors_captured[ 0 ]


def test_107_process_fragments_argument_with_doc_and_string( ):
    ''' _process_fragments_argument handles mixed Doc and string fragments. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    # Create fragments with both Doc objects and string references
    fragments = (
        interfaces_module.Doc( "Direct documentation content" ),
        "table_reference",
        interfaces_module.Doc( "Another direct doc" ),
    )
    table = {
        'table_reference': 'Content from table lookup',
        'unused_key': 'This should not appear',
    }
    result = assembly_module._process_fragments_argument(
        context, fragments, table
    )
    # Should process both types correctly
    assert len( result ) == 3
    assert 'Direct documentation content' in result
    assert 'Content from table lookup' in result
    assert 'Another direct doc' in result


def test_108_process_fragments_argument_missing_table_key( ):
    ''' _process_fragments_argument handles missing table keys. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
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
    fragments = ( "missing_key", "valid_key" )
    table = { 'valid_key': 'Valid content' }
    result = assembly_module._process_fragments_argument(
        context, fragments, table
    )
    # Should skip missing key and include valid one
    assert len( result ) == 1
    assert 'Valid content' in result
    # Should issue error for missing key
    assert len( errors_captured ) == 1
    assert 'not in provided table' in errors_captured[ 0 ]


def test_109_process_fragments_argument_invalid_fragment( ):
    ''' _process_fragments_argument handles invalid fragment types. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
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
    fragments = (
        interfaces_module.Doc( "Valid doc" ),
        42,  # Invalid type
        "valid_string",
        [ "invalid", "list" ],  # Invalid type
    )
    table = { 'valid_string': 'String content' }
    result = assembly_module._process_fragments_argument(
        context, fragments, table
    )
    # Should only process valid fragments
    assert len( result ) == 2
    assert 'Valid doc' in result
    assert 'String content' in result
    # Should issue errors for invalid types
    assert len( errors_captured ) == 2
    assert 'is invalid' in errors_captured[ 0 ]
    assert 'is invalid' in errors_captured[ 1 ]


def test_110_decorate_class_attributes_with_property( ):
    ''' _decorate_class_attributes handles properties with surface update. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    interfaces_module = cache_import_module( f"{PACKAGE_NAME}.interfaces" )
    renderers_module = cache_import_module(
        f"{PACKAGE_NAME}.renderers.sphinxad" )
    import inspect
    from typing import Annotated
    def proper_fragment_rectifier( fragment, source ):
        ''' Proper fragment rectifier that cleans docstrings. '''
        if source == interfaces_module.FragmentSources.Docstring:
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection = context_module.IntrospectionControl(
        targets = context_module.IntrospectionTargets.Descriptor
    )
    class TestClassWithProperty:
        @property
        def test_property( self ) -> Annotated[
            str,
            interfaces_module.Doc( "The current status value" ),
            interfaces_module.Raises( ValueError, "When status is corrupted" ),
            interfaces_module.Raises(
                RuntimeError, "When system is unavailable" )
        ]:
            ''' Property with basic docstring. '''
            return "test_value"
    original_docstring = TestClassWithProperty.test_property.__doc__
    assert original_docstring.strip() == 'Property with basic docstring.'
    assembly_module._decorate_class_attributes(
        TestClassWithProperty,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = renderers_module.produce_fragment,
        table = { }
    )
    updated_docstring = TestClassWithProperty.test_property.__doc__
    assert updated_docstring is not None
    assert updated_docstring != original_docstring
    assert 'Property with basic docstring.' in updated_docstring
    assert ':returns: The current status value' in updated_docstring
    assert ':raises ValueError: When status is corrupted' in updated_docstring
    assert ':raises RuntimeError: When system is unavailable' in (
        updated_docstring )


def test_111_decorate_class_attributes_introspection_disabled( ):
    ''' _decorate_class_attributes skips when introspection disabled. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    import inspect
    def proper_fragment_rectifier( fragment, source ):
        if source == 'docstring':
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection = context_module.IntrospectionControl( )
    class TestClassWithLimit:
        ''' Test class with introspection limit. '''
        _dynadoc_introspection_limit_ = context_module.IntrospectionLimit(
            disable = True
        )
        def test_method( self ):
            ''' Original method docstring. '''
            pass
        test_attribute = "test_value"
    original_method_doc = TestClassWithLimit.test_method.__doc__
    assembly_module._decorate_class_attributes(
        TestClassWithLimit,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, ctx: 'DECORATED',
        table = { }
    )
    # Method should retain original docstring since introspection was disabled
    assert TestClassWithLimit.test_method.__doc__ == original_method_doc


def test_112_decorate_module_attributes_introspection_disabled( ):
    ''' _decorate_module_attributes skips when introspection disabled. '''
    assembly_module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    context_module = cache_import_module( f"{PACKAGE_NAME}.context" )
    import types
    import inspect
    def proper_fragment_rectifier( fragment, source ):
        if source == 'docstring':
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    context = context_module.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True )
    )
    introspection = context_module.IntrospectionControl( )
    # Create a test module with an introspection limit that disables decoration
    test_module = types.ModuleType( 'test_module_with_limit' )
    test_module._dynadoc_introspection_limit_ = (
        context_module.IntrospectionLimit( disable = True )
    )
    def test_function( ):
        ''' Original function docstring. '''
        pass
    test_module.test_function = test_function
    test_module.test_variable = "test_value"
    original_function_doc = test_function.__doc__
    assembly_module._decorate_module_attributes(
        test_module,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, ctx: 'DECORATED',
        table = { }
    )
    # Function should retain original docstring since introspection disabled
    assert test_module.test_function.__doc__ == original_function_doc
