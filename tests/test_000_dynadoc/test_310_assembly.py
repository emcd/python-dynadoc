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


import inspect
import types

from dynadoc import assembly as module
from dynadoc import context as _context
from dynadoc import interfaces as _interfaces

from . import PACKAGE_NAME, cache_import_module


def test_100_assign_module_docstring_with_module_object( ):
    ''' assign_module_docstring accepts actual module objects. '''
    test_module = types.ModuleType( 'test_module' )
    test_module.__doc__ = 'Test module'
    module.assign_module_docstring( test_module )
    assert test_module.__doc__ == 'Test module'


def test_101_collect_fragments_invalid_sequence( ):
    ''' _collect_fragments handles invalid fragments sequence gracefully. '''
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error':
            errors_captured.append( message )
    context = _context.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    class InvalidFragmentsClass:
        _dynadoc_fragments_ = 42  # Integer is not a sequence
    obj = InvalidFragmentsClass( )
    result = module._collect_fragments( obj, context, 'test.fqname' )
    assert result == ( )
    assert len( errors_captured ) == 1
    assert 'Invalid fragments sequence' in errors_captured[ 0 ]


def test_102_collect_fragments_invalid_fragment_type( ):
    ''' _collect_fragments handles invalid fragment types in sequence. '''
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error': errors_captured.append( message )
    context = _context.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    class InvalidFragmentTypesClass:
        _dynadoc_fragments_ = (
            _interfaces.Doc( "Valid doc fragment" ),
            42,  # Invalid: not a string or Doc
            "valid string fragment",
            [ "invalid", "list" ],  # Invalid: not a string or Doc
        )
    obj = InvalidFragmentTypesClass( )
    result = module._collect_fragments( obj, context, 'test.fqname' )
    assert len( result ) == 4
    assert len( errors_captured ) == 2  # Two invalid fragments
    assert 'Invalid fragment' in errors_captured[ 0 ]
    assert 'Invalid fragment' in errors_captured[ 1 ]


def test_103_consider_class_attribute_module_recursion( ):
    ''' _consider_class_attribute handles module recursion correctly. '''
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl(
        targets = _context.IntrospectionTargets.Module )
    mock_submodule = types.ModuleType( 'test_module.submodule' )
    pmname = 'test_module'
    pqname = 'TestClass'
    aname = 'submodule_attr'
    result, update_surface = module._consider_class_attribute(
        mock_submodule, context, introspection, pmname, pqname, aname )
    assert result is mock_submodule
    assert update_surface == False


def test_104_decorate_object_already_visited( ):
    ''' _decorate handles objects already in visitees set. '''
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl( )
    @module.exclude
    class TestClass: pass
    try:
        module._decorate(
            TestClass,
            context = context,
            introspection = introspection,
            preserve = True,
            renderer = lambda obj, info, context: '',
            fragments = ( ),
            table = { } )
        assert True
    finally: module._visitees.discard( TestClass )


def test_105_decorate_core_introspection_disabled( ):
    ''' _decorate_core handles disabled introspection. '''
    def proper_fragment_rectifier( fragment, source ):
        ''' Proper fragment rectifier that cleans docstrings. '''
        if source == _interfaces.FragmentSources.Docstring:
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl( enable = False )
    def test_function( x: int ) -> str:
        ''' Test function. '''
        return str( x )
    module._decorate_core(
        test_function,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, ctx: ':introspected:',
        fragments = ( ),
        table = { } )
    assert test_function.__doc__ == 'Test function.'


def test_106_limit_introspection_invalid_limit( ):
    ''' _limit_introspection handles invalid introspection limit objects. '''
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error': errors_captured.append( message )
    context = _context.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl( )
    class InvalidLimitClass:
        _dynadoc_introspection_limit_ = "not a valid limit object"
    obj = InvalidLimitClass( )
    result = module._limit_introspection(
        obj, context, introspection, 'test.fqname' )
    assert result is introspection
    assert len( errors_captured ) == 1
    assert 'Invalid introspection limit' in errors_captured[ 0 ]


def test_107_process_fragments_argument_with_doc_and_string( ):
    ''' _process_fragments_argument handles mixed Doc and string fragments. '''
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    fragments = (
        _interfaces.Doc( "Direct documentation content" ),
        "table_reference",
        _interfaces.Doc( "Another direct doc" ),
    )
    table = {
        'table_reference': 'Content from table lookup',
        'unused_key': 'This should not appear',
    }
    result = module._process_fragments_argument(
        context, fragments, table )
    assert len( result ) == 3
    assert 'Direct documentation content' in result
    assert 'Content from table lookup' in result
    assert 'Another direct doc' in result


def test_108_process_fragments_argument_missing_table_key( ):
    ''' _process_fragments_argument handles missing table keys. '''
    module = cache_import_module( f"{PACKAGE_NAME}.assembly" )
    _context = cache_import_module( f"{PACKAGE_NAME}.context" )
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error': errors_captured.append( message )
    context = _context.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    fragments = ( "missing_key", "valid_key" )
    table = { 'valid_key': 'Valid content' }
    result = module._process_fragments_argument(
        context, fragments, table )
    assert len( result ) == 1
    assert 'Valid content' in result
    assert len( errors_captured ) == 1
    assert 'not in provided table' in errors_captured[ 0 ]


def test_109_process_fragments_argument_invalid_fragment( ):
    ''' _process_fragments_argument handles invalid fragment types. '''
    errors_captured = [ ]
    def capture_notifier( level, message ):
        if level == 'error': errors_captured.append( message )
    context = _context.Context(
        notifier = capture_notifier,
        fragment_rectifier = lambda fragment, source: fragment,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    fragments = (
        _interfaces.Doc( "Valid doc" ),
        42,  # Invalid type
        "valid_string",
        [ "invalid", "list" ],  # Invalid type
    )
    table = { 'valid_string': 'String content' }
    result = module._process_fragments_argument(
        context, fragments, table )
    assert len( result ) == 2
    assert 'Valid doc' in result
    assert 'String content' in result
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


def test_111_decorate_class_attributes_introspection_limiter_skip( ):
    ''' _decorate_class_attributes skips attributes when limiter disables. '''
    def proper_fragment_rectifier( fragment, source ):
        ''' Proper fragment rectifier that cleans docstrings. '''
        if source == _interfaces.FragmentSources.Docstring:
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    def _test_marker_limiter( objct, introspection ):
        ''' Limiter that disables introspection for objects with marker. '''
        if hasattr( objct, '_skip_introspection' ):
            limit = _context.IntrospectionLimit( disable = True )
            return introspection.with_limit( limit )
        return introspection
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl(
        targets = _context.IntrospectionTargets.Class,
        limiters = [ _test_marker_limiter ] )
    class TestClassWithNestedClasses:
        ''' Parent class with nested classes. '''
        class MarkedNestedClass:
            ''' This nested class should not be introspected. '''
            _skip_introspection = True
        class UnmarkedNestedClass:
            ''' This nested class should be introspected. '''
            pass
    marked_original = (
        TestClassWithNestedClasses.MarkedNestedClass.__doc__ )
    module._decorate_class_attributes(
        TestClassWithNestedClasses,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, context: ':introspected:',
        table = { } )
    assert TestClassWithNestedClasses.MarkedNestedClass.__doc__ == (
        marked_original )
    assert ':introspected:' in (
        TestClassWithNestedClasses.UnmarkedNestedClass.__doc__ )


def test_112_decorate_module_attributes_introspection_limiter_skip( ):
    ''' _decorate_module_attributes skips attributes when limiter disables. '''
    def proper_fragment_rectifier( fragment, source ):
        ''' Proper fragment rectifier that cleans docstrings. '''
        if source == _interfaces.FragmentSources.Docstring:
            return inspect.cleandoc( fragment ).rstrip( )
        return fragment
    def _test_marker_limiter( objct, introspection ):
        ''' Limiter that disables introspection for objects with marker. '''
        if hasattr( objct, '_skip_introspection' ):
            limit = _context.IntrospectionLimit( disable = True )
            return introspection.with_limit( limit )
        return introspection
    context = _context.Context(
        notifier = lambda level, msg: None,
        fragment_rectifier = proper_fragment_rectifier,
        visibility_decider = (
            lambda possessor, name, annotation, description: True ) )
    introspection = _context.IntrospectionControl(
        targets = _context.IntrospectionTargets.Class,
        limiters = [ _test_marker_limiter ] )
    test_module = types.ModuleType( 'test_module' )
    class MarkedClass:
        _skip_introspection = True
        def marked_method( self ):
            ''' This method should not be introspected. '''
            pass
    class UnmarkedClass:
        def unmarked_method( self ):
            ''' This method should be introspected. '''
            pass
    MarkedClass.__module__ = 'test_module'
    UnmarkedClass.__module__ = 'test_module'
    test_module.marked_attr = MarkedClass
    test_module.unmarked_attr = UnmarkedClass
    module._decorate_module_attributes(
        test_module,
        context = context,
        introspection = introspection,
        preserve = True,
        renderer = lambda obj, info, context: ':introspected:',
        table = { } )
    assert test_module.marked_attr.__doc__ is None
    assert ':introspected:' in test_module.unmarked_attr.__doc__
