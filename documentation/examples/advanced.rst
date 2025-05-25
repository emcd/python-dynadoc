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
renderers, sophisticated annotation patterns, error handling strategies,
performance optimization, and extension strategies for specialized documentation
needs.

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
    ... def process_api_request(
    ...     endpoint: Annotated[ str, dynadoc.Doc( "API endpoint URL to process" ) ],
    ...     timeout: Annotated[ float, dynadoc.Doc( "Request timeout in seconds" ) ] = 30.0,
    ... ) -> Annotated[ dict, dynadoc.Doc( "Processed API response data" ) ]:
    ...     ''' Process API request with custom Markdown rendering. '''
    ...     return { }
    >>>
    >>> print( process_api_request.__doc__ )
    Process API request with custom Markdown rendering.
    <BLANKLINE>
    - **endpoint** (`str`): API endpoint URL to process
    - **timeout** (`float`): Request timeout in seconds
    - **Returns** (`dict`): Processed API response data


Error Handling Strategies
===============================================================================

Different error handling strategies suit different development workflows and
deployment environments:


Basic Error Handling
-------------------------------------------------------------------------------

The default behavior issues warnings for most problems but continues processing:

.. doctest:: Advanced

    >>> def basic_notifier( level: str, message: str ) -> None:
    ...     ''' Basic notifier that prints warnings and errors. '''
    ...     print( f"[DYNADOC {level.upper()}] {message}" )
    >>>
    >>> basic_context = dynadoc.produce_context( notifier = basic_notifier )
    >>>
    >>> # Use with missing fragment reference to see error handling
    >>> fragments = { 'valid_key': 'This fragment exists' }
    >>>
    >>> @dynadoc.with_docstring( context = basic_context, table = fragments )
    ... def example_function(
    ...     param1: Annotated[ str, dynadoc.Fname( 'valid_key' ) ],
    ...     param2: Annotated[ int, dynadoc.Fname( 'missing_key' ) ],
    ... ) -> None:
    ...     ''' Example function with missing fragment reference. '''
    ...     pass
    [DYNADOC ERROR] Fragment 'missing_key' not in provided table.

The function processes successfully despite the missing fragment, issuing a
clear error message about the problem.


Strict Error Handling
-------------------------------------------------------------------------------

For development environments where you want immediate feedback on documentation
issues:

.. doctest:: Advanced

    >>> def strict_notifier( level: str, message: str ) -> None:
    ...     ''' Strict error handling that fails fast on any issues. '''
    ...     if level == 'error':
    ...         raise ValueError( f"Documentation error: {message}" )
    ...     elif level == 'admonition':
    ...         print( f"WARNING: {message}" )
    >>>
    >>> strict_context = dynadoc.produce_context( notifier = strict_notifier )

This approach catches documentation problems early in development, ensuring
clean documentation before deployment.


Development-Friendly Error Handling
-------------------------------------------------------------------------------

For development workflows that need detailed debugging information:

.. doctest:: Advanced

    >>> def development_notifier( level: str, message: str ) -> None:
    ...     ''' Development-friendly error handling with detailed output. '''
    ...     import sys
    ...     import traceback
    ...     timestamp = "2024-01-01 12:00:00"  # In real code, use datetime.now()
    ...     print( f"[{timestamp}] DYNADOC {level.upper()}: {message}", file = sys.stderr )
    ...     if level == 'error':
    ...         # In real development, you might want stack traces
    ...         print( f"  Context: Processing documentation generation", file = sys.stderr )
    >>>
    >>> dev_context = dynadoc.produce_context( notifier = development_notifier )

This provides rich context for debugging documentation generation issues during
development.


Production Error Handling
-------------------------------------------------------------------------------

For production environments where you want to log issues but never interrupt
application startup:

.. doctest:: Advanced

    >>> def production_notifier( level: str, message: str ) -> None:
    ...     ''' Production error handling that logs but doesn't interrupt. '''
    ...     # In real code, you'd use proper logging
    ...     if level == 'error':
    ...         # Log to error tracking system (e.g., Sentry, CloudWatch)
    ...         pass  # logger.error(f"Dynadoc error: {message}")
    ...     elif level == 'admonition':
    ...         # Log as warning
    ...         pass  # logger.warning(f"Dynadoc warning: {message}")
    >>>
    >>> prod_context = dynadoc.produce_context( notifier = production_notifier )

This ensures that documentation issues never prevent application deployment,
while still capturing problems for later investigation.


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
    ... class DataProcessingPipeline:
    ...     ''' Data processing pipeline with nested configuration classes. '''
    ...
    ...     max_workers: Annotated[ int, dynadoc.Doc( "Maximum number of worker threads" ) ]
    ...
    ...     class ProcessingConfig:
    ...         ''' Processing configuration that should have limited introspection. '''
    ...         batch_size: Annotated[ int, dynadoc.Doc( "Number of items per batch" ) ]
    >>>
    >>> print( DataProcessingPipeline.__doc__ )
    Data processing pipeline with nested configuration classes.
    <BLANKLINE>
    :ivar max_workers: Maximum number of worker threads
    :vartype max_workers: int

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
    ... class ConfigurationService:
    ...     ''' Demonstrates default visibility behavior. '''
    ...
    ...     # Public, documented - visible
    ...     api_endpoint: Annotated[ str, dynadoc.Doc( "Primary API endpoint URL" ) ]
    ...
    ...     # Public, undocumented - still visible (public API)
    ...     retry_count: int
    ...
    ...     # Private, documented - visible (intentionally exposed)
    ...     _debug_enabled: Annotated[ bool, dynadoc.Doc( "Internal debug flag for troubleshooting" ) ]
    ...
    ...     # Private, undocumented - hidden (truly internal)
    ...     _internal_cache: dict
    ...
    >>> print( ConfigurationService.__doc__ )
    Demonstrates default visibility behavior.
    <BLANKLINE>
    :ivar api_endpoint: Primary API endpoint URL
    :vartype api_endpoint: str
    :ivar retry_count:
    :vartype retry_count: int
    :ivar _debug_enabled: Internal debug flag for troubleshooting
    :vartype _debug_enabled: bool

Notice that ``_internal_cache`` doesn't appear because it lacks documentation,
indicating it's truly internal.


Explicit Visibility Control
-------------------------------------------------------------------------------

For fine-grained control, use ``Visibilities`` annotations to override the
default behavior:

.. doctest:: Advanced

    >>> @dynadoc.with_docstring( )
    ... class CacheManager:
    ...     ''' Demonstrates explicit visibility control. '''
    ...
    ...     # Force visibility for private attribute
    ...     _cache_stats: Annotated[
    ...         dict,
    ...         dynadoc.Doc( "Internal cache statistics for monitoring" ),
    ...         dynadoc.Visibilities.Reveal
    ...     ]
    ...
    ...     # Hide implementation detail from documentation
    ...     buffer_implementation: Annotated[
    ...         str,
    ...         dynadoc.Doc( "Internal buffer implementation details" ),
    ...         dynadoc.Visibilities.Conceal
    ...     ]
    ...
    ...     # Normal public attribute
    ...     cache_size: Annotated[ int, dynadoc.Doc( "Maximum number of cached items" ) ]
    ...
    >>> print( CacheManager.__doc__ )
    Demonstrates explicit visibility control.
    <BLANKLINE>
    :ivar _cache_stats: Internal cache statistics for monitoring
    :vartype _cache_stats: dict
    :ivar cache_size: Maximum number of cached items
    :vartype cache_size: int

The ``Visibilities`` annotations take precedence over both default rules and
custom visibility deciders.


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
    ... class PublicAPIClient:
    ...     ''' API client with strict visibility rules. '''
    ...
    ...     documented_endpoint: Annotated[ str, dynadoc.Doc( "Public API endpoint" ) ]
    ...     undocumented_setting: str  # No documentation
    ...     _private_config: Annotated[ str, dynadoc.Doc( "Private but documented" ) ]
    >>>
    >>> print( PublicAPIClient.__doc__ )
    API client with strict visibility rules.
    <BLANKLINE>
    :ivar documented_endpoint: Public API endpoint
    :vartype documented_endpoint: str

The custom decider hides both ``undocumented_setting`` (no description) and
``_private_config`` (private name), creating stricter API documentation.


Controlling Attribute Value Display
===============================================================================

Sometimes you want to control how attribute values appear in documentation,
especially for complex objects that don't render well or when you want to
provide more descriptive information. The ``Default`` annotation provides
control over value display:

.. doctest:: Advanced

    >>> @dynadoc.with_docstring( )
    ... class ServiceConfiguration:
    ...     ''' Service configuration with controlled value display. '''
    ...
    ...     # Normal value display
    ...     service_version: Annotated[ str, dynadoc.Doc( "Current service version" ) ] = "v2.1"
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
    >>> print( ServiceConfiguration.__doc__ )
    Service configuration with controlled value display.
    <BLANKLINE>
    :ivar service_version: Current service version
    :vartype service_version: str
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


Extension Patterns
===============================================================================

Building extensions on top of ``dynadoc`` enables specialized functionality.
Here are some practical patterns for extending the library:


Domain-Specific Renderers
-------------------------------------------------------------------------------

Create renderers tailored to specific domains or output formats:

.. code-block:: python

    def rest_api_renderer( possessor, informations, context ):
        ''' Specialized renderer for REST API documentation. '''

        lines = [ ]
        for info in informations:
            if isinstance( info, ArgumentInformation ):
                # Format API parameters with HTTP context
                if info.name in ( 'method', 'endpoint', 'headers' ):
                    lines.append( f":http-param {info.name}: {info.description}" )
                else:
                    lines.append( f":param {info.name}: {info.description}" )
            elif isinstance( info, ReturnInformation ):
                # Format API responses
                lines.append( f":returns: {info.description}" )
                lines.append( f":response-type: {format_type( info.annotation )}" )

        return '\n'.join( lines )


Configuration Management Extensions
-------------------------------------------------------------------------------

Build configuration systems on top of ``dynadoc`` for consistent documentation
across teams:

.. code-block:: python

    class DocumentationStandards:
        ''' Company-wide documentation standards. '''

        @staticmethod
        def create_api_context( ):
            return dynadoc.produce_context(
                notifier = standards_notifier,
                fragment_rectifier = corporate_rectifier,
                visibility_decider = public_api_visibility
            )

        @staticmethod
        def create_internal_context( ):
            return dynadoc.produce_context(
                notifier = development_notifier,
                fragment_rectifier = relaxed_rectifier,
                visibility_decider = internal_visibility
            )


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

**Use error handling strategically** - Choose error handling approaches that
match your development workflow and deployment requirements.

**Leverage visibility control** - Use the multiple layers of visibility control
to create clean, focused API documentation that serves your users' needs.
