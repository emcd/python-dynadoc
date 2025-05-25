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
Advanced Topics
*******************************************************************************


Introduction
===============================================================================

This section covers advanced usage patterns for ``dynadoc``, including custom
renderers, sophisticated annotation patterns, performance optimization, and
extension strategies for specialized documentation needs.

.. doctest:: Advanced

    >>> import dynadoc
    >>> import dynadoc.xtnsapi as xtnsapi
    >>> from typing import Annotated


Custom Renderers
===============================================================================

While the built-in Sphinx renderer handles most use cases, you can create
custom renderers for different output formats or specialized documentation
styles:

.. doctest:: Advanced

    >>> def markdown_renderer( possessor, informations, context ):
    ...     ''' Custom renderer that outputs Markdown format. '''
    ...     lines = [ ]
    ...
    ...     for info in informations:
    ...         if isinstance( info, xtnsapi.ArgumentInformation ):
    ...             name = info.name
    ...             type_name = info.annotation.__name__ if hasattr( info.annotation, '__name__' ) else str( info.annotation )
    ...             description = info.description or 'No description'
    ...             lines.append( f"- **{name}** (`{type_name}`): {description}" )
    ...         elif isinstance( info, xtnsapi.ReturnInformation ):
    ...             type_name = info.annotation.__name__ if hasattr( info.annotation, '__name__' ) else str( info.annotation )
    ...             description = info.description or 'No description'
    ...             lines.append( f"- **Returns** (`{type_name}`): {description}" )
    ...
    ...     return '\n'.join( lines )
    >>>
    >>> @dynadoc.with_docstring( renderer = markdown_renderer )
    ... def example_function(
    ...     value: Annotated[ int, dynadoc.Doc( "Input value to process" ) ],
    ...     multiplier: Annotated[ float, dynadoc.Doc( "Multiplication factor" ) ] = 2.0,
    ... ) -> Annotated[ float, dynadoc.Doc( "Calculated result" ) ]:
    ...     ''' Example function with custom Markdown rendering. '''
    ...     return value * multiplier
    >>>
    >>> print( example_function.__doc__ )
    Example function with custom Markdown rendering.
    <BLANKLINE>
    - **value** (`int`): Input value to process
    - **multiplier** (`float`): Multiplication factor
    - **Returns** (`float`): Calculated result


Custom Introspection Limiters
===============================================================================

Custom introspection limiters provide fine-grained control over how deeply
``dynadoc`` introspects different objects. Limiters are functions that can
modify introspection behavior based on the specific object being documented:

.. doctest:: Advanced

    >>> def depth_limiter(
    ...     objct: object,
    ...     introspection: dynadoc.IntrospectionControl
    ... ) -> dynadoc.IntrospectionControl:
    ...     ''' Limits introspection depth for nested classes. '''
    ...     import inspect
    ...
    ...     # If this is a nested class, disable further class introspection
    ...     if inspect.isclass( objct ) and '.' in getattr( objct, '__qualname__', '' ):
    ...         limit = dynadoc.IntrospectionLimit(
    ...             targets_exclusions = dynadoc.IntrospectionTargets.Class
    ...         )
    ...         return introspection.with_limit( limit )
    ...
    ...     return introspection
    >>>
    >>> # Configure introspection with the custom limiter
    >>> introspection_with_limiter = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargetsSansModule,
    ...     limiters = ( depth_limiter, )
    ... )
    >>>
    >>> @dynadoc.with_docstring( introspection = introspection_with_limiter )
    ... class OuterClass:
    ...     ''' Outer class with nested classes. '''
    ...
    ...     value: Annotated[ int, dynadoc.Doc( "Outer class value" ) ]
    ...
    ...     class InnerClass:
    ...         ''' Inner class that should have limited introspection. '''
    ...         inner_value: Annotated[ str, dynadoc.Doc( "Inner class value" ) ]
    >>>
    >>> print( OuterClass.__doc__ )
    Outer class with nested classes.
    <BLANKLINE>
    :ivar value: Outer class value
    :vartype value: int

The depth limiter prevents recursive introspection of nested classes, avoiding
potential infinite loops and controlling documentation scope for complex class
hierarchies. Similar limiters can be created for performance optimization,
domain-specific documentation policies, or handling special object types.


Visibility Control
===============================================================================

The ``dynadoc`` library provides multiple layers of visibility control to
determine which attributes appear in documentation. Understanding these rules
helps you create clean, comprehensive API documentation.


Attribute Visibility Rules
-------------------------------------------------------------------------------

The library uses intuitive default visibility rules:

- **Public attributes** (not starting with ``_``) are always visible
- **Private attributes** are visible only if they have documentation
- **Explicit visibility annotations** override these rules

This design reflects a key principle: *if you document a private attribute,
you're signaling it's important enough for users to know about.*

.. doctest:: Advanced

    >>> @dynadoc.with_docstring( )
    ... class VisibilityExample:
    ...     ''' Demonstrates default visibility behavior. '''
    ...
    ...     # Public, documented - visible
    ...     public_documented: Annotated[ str, dynadoc.Doc( "Public API method" ) ]
    ...
    ...     # Public, undocumented - still visible (public API)
    ...     public_undocumented: int
    ...
    ...     # Private, documented - visible (intentionally exposed)
    ...     _private_documented: Annotated[ bool, dynadoc.Doc( "Important internal flag" ) ]
    ...
    ...     # Private, undocumented - hidden (truly internal)
    ...     _private_undocumented: float
    ...
    >>> print( VisibilityExample.__doc__ )
    Demonstrates default visibility behavior.
    <BLANKLINE>
    :ivar public_documented: Public API method
    :vartype public_documented: str
    :ivar public_undocumented:
    :vartype public_undocumented: int
    :ivar _private_documented: Important internal flag
    :vartype _private_documented: bool

Notice that ``_private_undocumented`` doesn't appear because it lacks
documentation, indicating it's truly internal.


Explicit Visibility Control
-------------------------------------------------------------------------------

For fine-grained control, use ``Visibilities`` annotations to override the
default behavior:

.. doctest:: Advanced

    >>> @dynadoc.with_docstring( )
    ... class ExplicitVisibility:
    ...     ''' Demonstrates explicit visibility control. '''
    ...
    ...     # Force visibility for private attribute
    ...     _debug_info: Annotated[
    ...         dict,
    ...         dynadoc.Doc( "Debug information for troubleshooting" ),
    ...         dynadoc.Visibilities.Reveal
    ...     ]
    ...
    ...     # Hide public attribute from documentation
    ...     api_secret: Annotated[
    ...         str,
    ...         dynadoc.Doc( "Secret key - hidden for security" ),
    ...         dynadoc.Visibilities.Conceal
    ...     ]
    ...
    ...     # Normal public attribute
    ...     app_name: Annotated[ str, dynadoc.Doc( "Application name" ) ]
    ...
    >>> print( ExplicitVisibility.__doc__ )
    Demonstrates explicit visibility control.
    <BLANKLINE>
    :ivar _debug_info: Debug information for troubleshooting
    :vartype _debug_info: dict
    :ivar app_name: Application name
    :vartype app_name: str

The ``Visibilities`` annotations take precedence over both default rules and
custom visibility deciders.


Module __all__ Support
-------------------------------------------------------------------------------

For modules, ``dynadoc`` automatically respects ``__all__`` declarations when
present, overriding the default visibility rules:

.. code-block:: python

    # When __all__ is present, only listed attributes are documented
    __all__ = [ 'public_function', 'IMPORTANT_CONSTANT' ]

    # This will be documented (in __all__)
    public_function: Annotated[ callable, dynadoc.Doc( "Public API function" ) ]

    # This will NOT be documented (not in __all__)
    helper_function: Annotated[ callable, dynadoc.Doc( "Internal helper" ) ]

When ``__all__`` is absent, the library uses the standard visibility rules
described above.


Custom Visibility Deciders
-------------------------------------------------------------------------------

For advanced scenarios, you can implement custom visibility logic that replaces
the default rules (but is still overridden by explicit ``Visibilities``
annotations):

.. doctest:: Advanced

    >>> def api_visibility_decider( possessor, name: str, annotation, description ):
    ...     ''' Custom visibility for API documentation. '''
    ...     import inspect
    ...
    ...     # Always hide private names
    ...     if name.startswith( '_' ):
    ...         return False
    ...
    ...     # For modules, respect __all__ if present
    ...     if inspect.ismodule( possessor ):
    ...         all_list = getattr( possessor, '__all__', None )
    ...         if all_list is not None:
    ...             return name in all_list
    ...
    ...     # Only show documented public attributes
    ...     return bool( description )
    >>>
    >>> api_context = dynadoc.produce_context(
    ...     visibility_decider = api_visibility_decider
    ... )
    >>>
    >>> @dynadoc.with_docstring( context = api_context )
    ... class APIClass:
    ...     ''' API class with custom visibility rules. '''
    ...
    ...     documented_attr: Annotated[ str, dynadoc.Doc( "API attribute" ) ]
    ...     undocumented_attr: str  # No documentation
    ...     _private_attr: Annotated[ str, dynadoc.Doc( "Private but documented" ) ]
    ...
    >>> print( APIClass.__doc__ )
    API class with custom visibility rules.
    <BLANKLINE>
    :ivar documented_attr: API attribute
    :vartype documented_attr: str

The custom decider hides both ``undocumented_attr`` (no description) and
``_private_attr`` (private name), creating stricter API documentation.


Visibility Precedence Order
-------------------------------------------------------------------------------

The visibility system follows this precedence order (highest to lowest):

1. **Explicit annotations** (``Visibilities.Conceal/Reveal``)
2. **Custom visibility deciders** (when provided in context)
3. **Module __all__** (for module attributes only)
4. **Default rules** (public always visible, private only if documented)

Understanding this hierarchy helps you combine different visibility mechanisms
effectively for sophisticated documentation policies.


Controlling Attribute Value Display
===============================================================================

Sometimes you want to control how attribute values appear in documentation,
especially for complex objects that don't render well or when you want to
provide more descriptive information. The ``Default`` annotation provides
control over value display:

.. doctest:: Advanced

    >>> @dynadoc.with_docstring( )
    ... class ConfigurationManager:
    ...     ''' Manages application configuration with controlled value display. '''
    ...
    ...     # Normal value display
    ...     version: Annotated[ str, dynadoc.Doc( "Current version" ) ] = "v2.1"
    ...
    ...     # Suppress value display for function objects
    ...     error_handler: Annotated[
    ...         callable,
    ...         dynadoc.Doc( "Default error handling function" ),
    ...         dynadoc.Default( mode = dynadoc.ValuationModes.Suppress )
    ...     ] = lambda error: print( f"Error: {error}" )
    ...
    ...     # Use surrogate description instead of actual value
    ...     database_config: Annotated[
    ...         dict,
    ...         dynadoc.Doc( "Database connection configuration" ),
    ...         dynadoc.Default(
    ...             mode = dynadoc.ValuationModes.Surrogate,
    ...             surrogate = "Loaded from environment variables"
    ...         )
    ...     ] = { "host": "localhost", "database": "prod_db" }
    ...
    >>> print( ConfigurationManager.__doc__ )
    Manages application configuration with controlled value display.
    <BLANKLINE>
    :ivar version: Current version
    :vartype version: str
    :ivar error_handler: Default error handling function
    :vartype error_handler: callable
    :ivar database_config: Database connection configuration
    :vartype database_config: dict

The ``ValuationModes`` provide three options:

- **Accept** (default): Show the actual attribute value
- **Suppress**: Hide the value entirely (useful for function objects, complex instances)
- **Surrogate**: Display an alternative description instead of the actual value

This is particularly useful when you want to document the purpose of attributes
without exposing implementation details like function memory addresses or when
you want to provide more meaningful descriptions than the raw data structure.

.. doctest:: Advanced

    >>> def api_visibility_decider( possessor, name: str, annotation, description ):
    ...     ''' Visibility decider for public API documentation. '''
    ...     import inspect
    ...
    ...     # Always hide private names
    ...     if name.startswith( '_' ):
    ...         return False
    ...
    ...     # For modules, respect __all__ if present
    ...     if inspect.ismodule( possessor ):
    ...         all_list = getattr( possessor, '__all__', None )
    ...         if all_list is not None:
    ...             return name in all_list
    ...
    ...     # Default: show only documented public attributes
    ...     return bool( description )
    >>>
    >>> # Context with strict API visibility
    >>> api_context = dynadoc.produce_context(
    ...     visibility_decider = api_visibility_decider
    ... )
    >>>
Error Handling Strategies
===============================================================================

Different error handling strategies suit different development workflows:

.. doctest:: Advanced

    >>> def strict_notifier( level: str, message: str ) -> None:
    ...     ''' Strict error handling that fails fast on any issues. '''
    ...     if level == 'error':
    ...         raise ValueError( f"Documentation error: {message}" )
    ...     elif level == 'admonition':
    ...         print( f"WARNING: {message}" )
    >>>
    >>> def development_notifier( level: str, message: str ) -> None:
    ...     ''' Development-friendly error handling with detailed output. '''
    ...     import sys
    ...     print( f"[DYNADOC {level.upper()}] {message}", file = sys.stderr )
    >>>
    >>> def production_notifier( level: str, message: str ) -> None:
    ...     ''' Production error handling that logs but doesn't interrupt. '''
    ...     # In real code, you'd use proper logging
    ...     if level == 'error':
    ...         pass  # Log to error tracking system
    ...     # Silently ignore warnings in production
    >>>
    >>> # Example usage in different environments
    >>> dev_context = dynadoc.produce_context( notifier = development_notifier )
    >>> prod_context = dynadoc.produce_context( notifier = production_notifier )

Choose the appropriate error handling strategy based on your environment and
tolerance for documentation issues.


Performance Optimization
===============================================================================

For large codebases, strategic configuration can improve documentation
generation performance:

.. code-block:: python

    # Minimal introspection for faster processing
    fast_introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function  # Only functions
    )

    # Lightweight context with minimal processing
    fast_context = dynadoc.produce_context(
        notifier = lambda level, msg: None,  # Silent operation
        fragment_rectifier = lambda fragment, source: fragment  # No processing
    )

    # Apply to modules without recursion
    dynadoc.assign_module_docstring(
        __name__,
        context = fast_context,
        introspection = fast_introspection
    )

**Performance considerations:**

- **Limit introspection targets** to only what you need
- **Avoid deep recursion** in large package hierarchies
- **Use simple renderers** for better performance
- **Cache contexts** when documenting multiple modules
- **Profile documentation generation** for bottlenecks


Documentation Generation Pipelines
===============================================================================

Complex projects may require multi-stage documentation pipelines:

.. code-block:: python

    def generate_api_docs( module_name: str ) -> str:
        ''' Generate API documentation with multiple passes. '''

        # Stage 1: Collect all fragments
        fragments = collect_project_fragments( module_name )

        # Stage 2: Configure for API documentation
        api_context = dynadoc.produce_context(
            notifier = strict_error_handler,
            fragment_rectifier = api_fragment_processor,
            visibility_decider = public_api_filter
        )

        # Stage 3: Apply comprehensive introspection
        api_introspection = dynadoc.IntrospectionControl(
            targets = dynadoc.IntrospectionTargetsSansModule,
            class_control = dynadoc.ClassIntrospectionControl(
                inheritance = True,
                scan_attributes = True
            )
        )

        # Stage 4: Generate documentation
        dynadoc.assign_module_docstring(
            module_name,
            context = api_context,
            introspection = api_introspection,
            table = fragments
        )

        return "Documentation generated successfully"

This multi-stage approach allows for sophisticated documentation workflows
tailored to specific project requirements.


Extension Patterns
===============================================================================

Building extensions on top of ``dynadoc`` enables specialized functionality:

.. code-block:: python

    class DocumentationBuilder:
        ''' Builder pattern for complex documentation configurations. '''

        def __init__( self ):
            self.fragments = { }
            self.context_config = { }
            self.introspection_config = { }

        def add_fragments( self, fragment_dict: dict ) -> 'DocumentationBuilder':
            self.fragments.update( fragment_dict )
            return self

        def with_custom_renderer( self, renderer ) -> 'DocumentationBuilder':
            self.context_config[ 'renderer' ] = renderer
            return self

        def enable_inheritance( self ) -> 'DocumentationBuilder':
            if 'class_control' not in self.introspection_config:
                self.introspection_config[ 'class_control' ] = { }
            self.introspection_config[ 'class_control' ][ 'inheritance' ] = True
            return self

        def build( self ):
            ''' Build and return configured documentation components. '''
            context = dynadoc.produce_context( **self.context_config )
            introspection = dynadoc.IntrospectionControl( **self.introspection_config )
            return context, introspection, self.fragments

    # Usage example:
    # context, introspection, fragments = (
    #     DocumentationBuilder()
    #     .add_fragments( common_fragments )
    #     .with_custom_renderer( markdown_renderer )
    #     .enable_inheritance()
    #     .build()
    # )

This builder pattern provides a fluent interface for complex documentation
setups while maintaining type safety and clear configuration intent.


Best Practices for Advanced Usage
===============================================================================

When implementing advanced ``dynadoc`` patterns:

**Design for maintainability** - Keep custom renderers and configurations simple
and well-documented.

**Test thoroughly** - Advanced configurations can have subtle interactions, so
comprehensive testing is essential.

**Profile performance** - Custom renderers and complex introspection can impact
build times, especially in large projects.

**Document your extensions** - Custom patterns should be well-documented for
team members and future maintenance.

**Consider backward compatibility** - When building on ``dynadoc``, ensure your
extensions can adapt to library updates.

**Start simple and evolve** - Begin with basic configurations and add complexity
only when needed to solve specific problems.
