.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+


*******************************************************************************
Configuration
*******************************************************************************


Introduction
===============================================================================

The ``dynadoc`` library provides extensive configuration options through
``Context`` objects and ``IntrospectionControl`` settings. These allow you to
customize how annotations are processed, how errors are handled, which objects
are recursively documented, and how the final documentation is rendered.

.. doctest:: Configuration

    >>> import dynadoc
    >>> from typing import Annotated


Context Objects
===============================================================================

A ``Context`` object controls the overall behavior of documentation generation.
The library provides sensible defaults, but you can customize various aspects:

.. doctest:: Configuration

    >>> # Create a custom context with different error handling
    >>> def custom_notifier( level: str, message: str ) -> None:
    ...     print( f"[{level.upper()}] {message}" )
    >>>
    >>> custom_context = dynadoc.produce_context( notifier = custom_notifier )
    >>>
    >>> # Use the custom context with missing fragment references
    >>> fragments = { 'existing key': 'This fragment exists' }
    >>>
    >>> @dynadoc.with_docstring( context = custom_context, table = fragments )
    ... def example_function(
    ...     param: Annotated[ str, dynadoc.Fname( 'missing key' ) ]
    ... ) -> None:
    ...     ''' Example with missing fragment. '''
    ...     pass
    [ERROR] Fragment 'missing key' not in provided table.

The custom notifier receives error notifications and can handle them differently
than the default warning system.


Fragment Rectification
===============================================================================

Fragment rectifiers clean and normalize documentation text based on its source.
You can provide custom rectification logic:

.. doctest:: Configuration

    >>> def custom_rectifier( fragment: str, source ) -> str:
    ...     ''' Custom rectifier that adds prefixes based on source. '''
    ...     match source:
    ...         case dynadoc.FragmentSources.Annotation:
    ...             return f"Parameter: {fragment}"
    ...         case dynadoc.FragmentSources.Docstring:
    ...             return fragment.strip( ).upper( )
    ...         case _:
    ...             return fragment
    >>>
    >>> custom_context = dynadoc.produce_context(
    ...     fragment_rectifier = custom_rectifier
    ... )
    >>>
    >>> @dynadoc.with_docstring( context = custom_context )
    ... def demo_function(
    ...     value: Annotated[ int, dynadoc.Doc( "input number" ) ]
    ... ) -> None:
    ...     ''' processes the input value. '''
    ...     pass
    >>>
    >>> print( demo_function.__doc__ )
    PROCESSES THE INPUT VALUE.
    <BLANKLINE>
    :argument value: Parameter: input number
    :type value: int

The custom rectifier transforms the docstring to uppercase and adds "Parameter:"
prefix to argument descriptions.


Introspection Control
===============================================================================

``IntrospectionControl`` objects determine which objects are recursively
documented and how deeply the introspection proceeds:

.. doctest:: Configuration

    >>> # Create introspection control for comprehensive documentation
    >>> comprehensive_introspection = dynadoc.IntrospectionControl(
    ...     targets = (
    ...         dynadoc.IntrospectionTargets.Function |
    ...         dynadoc.IntrospectionTargets.Class |
    ...         dynadoc.IntrospectionTargets.Descriptor
    ...     )
    ... )
    >>>
    >>> # Note: the above is equivalent to:
    >>> # comprehensive_introspection = dynadoc.IntrospectionControl(
    >>> #     targets = dynadoc.IntrospectionTargetsSansModule
    >>> # )
    >>>
    >>> # Create a class with methods and properties
    >>> @dynadoc.with_docstring( introspection = comprehensive_introspection )
    ... class DataProcessor:
    ...     ''' Processes various types of data. '''
    ...
    ...     def process(
    ...         self,
    ...         data: Annotated[ list, dynadoc.Doc( "Input data to process" ) ]
    ...     ) -> Annotated[ dict, dynadoc.Doc( "Processed results" ) ]:
    ...         ''' Process input data and return results. '''
    ...         return { }
    ...
    ...     @property
    ...     def status( self ) -> Annotated[ str, dynadoc.Doc( "Current processor status" ) ]:
    ...         ''' Get the current status. '''
    ...         return "ready"

The comprehensive introspection automatically documents both the method and
property:

.. code-block:: text

    >>> print( DataProcessor.process.__doc__ )
    Process input data and return results.

    :argument self:
    :argument data: Input data to process
    :type data: list
    :returns: Processed results
    :rtype: dict

.. code-block:: text

    >>> print( DataProcessor.status.__doc__ )
    Get the current status.

    :returns: Current processor status
    :rtype: str


Selective Introspection
===============================================================================

You can create more targeted introspection controls for specific use cases:

.. doctest:: Configuration

    >>> # Only document functions, not classes or descriptors
    >>> functions_only = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargets.Function
    ... )
    >>>
    >>> # Only document classes, not their methods
    >>> classes_only = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargets.Class
    ... )
    >>>
    >>> # Document everything except modules (avoids recursing into submodules)
    >>> everything_but_modules = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargetsSansModule
    ... )

These targeted controls allow fine-grained control over documentation scope,
useful for different documentation strategies or performance considerations.


Class Introspection Controls
===============================================================================

Class introspection behavior can be customized with additional settings:

.. doctest:: Configuration

    >>> # Enable inheritance scanning for comprehensive class documentation
    >>> inheritance_introspection = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargets.Class,
    ...     class_control = dynadoc.ClassIntrospectionControl(
    ...         inheritance = True,
    ...         scan_attributes = True
    ...     )
    ... )

This configuration tells the introspector to:
- Include inherited annotations from parent classes
- Scan for attributes not covered by annotations


Custom Visibility Decisions
===============================================================================

You can customize which attributes are visible in documentation by providing
a custom visibility decider:

.. doctest:: Configuration

    >>> def strict_visibility( possessor, name: str, annotation, description ) -> bool:
    ...     ''' Only show attributes that have descriptions. '''
    ...     return bool( description )
    >>>
    >>> strict_context = dynadoc.produce_context(
    ...     visibility_decider = strict_visibility
    ... )
    >>>
    >>> @dynadoc.with_docstring( context = strict_context )
    ... class StrictExample:
    ...     ''' Example of strict visibility with class attributes. '''
    ...
    ...     documented: Annotated[ str, dynadoc.Doc( "This attribute has a description" ) ]
    ...     undocumented: int  # No Doc annotation
    >>>
    >>> print( StrictExample.__doc__ )
    Example of strict visibility with class attributes.
    <BLANKLINE>
    :ivar documented: This attribute has a description
    :vartype documented: str

Only the parameter with a description appears in the documentation, even though
both parameters have type annotations.


Annotation Resolution
===============================================================================

The context can be configured with different globals and locals for resolving
string annotations:

.. code-block:: python

    # Example: Custom resolution context for a module
    custom_globals = {
        'CustomType': MyCustomClass,
        'SpecialAlias': dict[ str, Any ],
    }

    resolution_context = dynadoc.produce_context(
        resolver_globals = custom_globals,
        resolver_locals = local_scope_vars
    )

    dynadoc.assign_module_docstring(
        __name__,
        context = resolution_context
    )

This allows proper resolution of forward references and string annotations that
reference types not available in the default scope.


Combining Configurations
===============================================================================

Multiple configuration options can be combined for sophisticated documentation
strategies:

.. doctest:: Configuration

    >>> # Comprehensive configuration example
    >>> def production_notifier( level: str, message: str ) -> None:
    ...     if level == 'error':
    ...         raise RuntimeError( f"Documentation error: {message}" )
    ...     print( f"Warning: {message}" )
    >>>
    >>> def clean_rectifier( fragment: str, source ) -> str:
    ...     ''' Clean and normalize all fragments consistently. '''
    ...     cleaned = fragment.strip( )
    ...     if cleaned and not cleaned.endswith( '.' ):
    ...         cleaned += '.'
    ...     return cleaned
    >>>
    >>> production_context = dynadoc.produce_context(
    ...     notifier = production_notifier,
    ...     fragment_rectifier = clean_rectifier
    ... )
    >>>
    >>> production_introspection = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargetsSansModule,
    ...     class_control = dynadoc.ClassIntrospectionControl( inheritance = True )
    ... )

This production configuration ensures strict error handling, consistent
formatting, and comprehensive documentation coverage.


Real-World Configuration Examples
===============================================================================

Here are some practical configuration patterns for different scenarios:

**API Documentation** - Comprehensive coverage with strict error handling:

.. code-block:: python

    api_context = dynadoc.produce_context(
        notifier = lambda level, msg: None if level == 'admonition' else print(msg)
    )

    api_introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargetsSansModule,
        class_control = dynadoc.ClassIntrospectionControl(
            inheritance = True,
            scan_attributes = True
        )
    )

**Internal Documentation** - Relaxed settings for development:

.. code-block:: python

    dev_context = dynadoc.produce_context(
        notifier = lambda level, msg: print(f"[DEV] {msg}")
    )

    dev_introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function
    )

**Library Documentation** - High-quality output with custom formatting:

.. code-block:: python

    def library_rectifier(fragment: str, source) -> str:
        # Add consistent punctuation and formatting
        cleaned = fragment.strip()
        match source:
            case dynadoc.FragmentSources.Annotation:
                cleaned = cleaned[0].lower() + cleaned[1:] if len(cleaned) > 1 else cleaned.lower()
        return cleaned

    library_context = dynadoc.produce_context(
        fragment_rectifier = library_rectifier
    )


Configuration Best Practices
===============================================================================

When configuring ``dynadoc``:

**Start with defaults** and only customize what you need::

    # Good: minimal necessary customization
    context = dynadoc.produce_context( notifier = custom_notifier )

**Use targeted introspection** to control documentation scope::

    # Good: specific targets for clear intent
    introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function
    )

**Test configuration changes** with representative code to ensure they work
as expected.

**Document your configuration choices** so team members understand the
documentation generation strategy.

**Consider performance** when enabling comprehensive introspection on large
codebases - start narrow and expand as needed.
