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
Fragments
*******************************************************************************


Introduction
===============================================================================

The ``dynadoc`` library provides a powerful fragment system for reusing
documentation text across multiple functions, classes, and modules. Instead of
repeating the same descriptions, you can define them once in a fragment table
and reference them using ``Fname`` annotations.

.. doctest:: Fragments

    >>> import dynadoc
    >>> from typing import Annotated


Basic Fragment Tables
===============================================================================

A fragment table is simply a dictionary mapping string keys to documentation
text. This allows you to define common descriptions once and reuse them:

.. doctest:: Fragments

    >>> # Define a fragment table with common descriptions
    >>> api_fragments = {
    ...     'api key': 'Authentication key for API access',
    ...     'timeout': 'Request timeout in seconds',
    ...     'retry count': 'Number of retry attempts before giving up',
    ...     'success status': 'Whether the operation completed successfully',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = api_fragments )
    ... def authenticate_user(
    ...     api_key: Annotated[ str, dynadoc.Fname( 'api key' ) ],
    ...     timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ] = 30.0,
    ... ) -> Annotated[ bool, dynadoc.Fname( 'success status' ) ]:
    ...     ''' Authenticate user with API credentials. '''
    ...     return True
    ...
    >>> print( authenticate_user.__doc__ )
    Authenticate user with API credentials.
    <BLANKLINE>
    :argument api_key: Authentication key for API access
    :type api_key: str
    :argument timeout: Request timeout in seconds
    :type timeout: float
    :returns: Whether the operation completed successfully
    :rtype: bool

Notice how ``Fname( 'api key' )`` references the ``'api key'`` key in the
fragment table, automatically substituting the full description.


Combining Doc and Fname
===============================================================================

You can mix ``Doc`` and ``Fname`` annotations in the same function, providing
flexibility for both specific and reusable descriptions:

.. doctest:: Fragments

    >>> @dynadoc.with_docstring( table = api_fragments )
    ... def retry_request(
    ...     endpoint_url: Annotated[ str, dynadoc.Doc( "Specific API endpoint URL to retry" ) ],
    ...     max_retries: Annotated[ int, dynadoc.Fname( 'retry count' ) ],
    ...     timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ] = 60.0,
    ... ) -> Annotated[ bool, dynadoc.Fname( 'success status' ) ]:
    ...     ''' Retry a failed API request with configurable parameters. '''
    ...     return True
    ...
    >>> print( retry_request.__doc__ )
    Retry a failed API request with configurable parameters.
    <BLANKLINE>
    :argument endpoint_url: Specific API endpoint URL to retry
    :type endpoint_url: str
    :argument max_retries: Number of retry attempts before giving up
    :type max_retries: int
    :argument timeout: Request timeout in seconds
    :type timeout: float
    :returns: Whether the operation completed successfully
    :rtype: bool


Module-Level Fragments
===============================================================================

Fragment tables are particularly useful for module-level documentation where
multiple functions share common parameter patterns:

.. code-block:: python

    # http_client.py
    ''' HTTP client utilities for API communication. '''

    import dynadoc
    from typing import Annotated

    # Define fragments for common HTTP concepts
    HTTP_FRAGMENTS = {
        'base url': 'Base URL for all API requests',
        'request timeout': 'Maximum time to wait for request completion in seconds',
        'session id': 'Unique identifier for the HTTP session',
        'response data': 'Parsed response data from the server',
        'headers dict': 'Dictionary of HTTP headers to include in request',
    }

    def create_session(
        base_url: Annotated[ str, dynadoc.Fname( 'base url' ) ],
        timeout: Annotated[ float, dynadoc.Fname( 'request timeout' ) ] = 30.0,
    ) -> Annotated[ str, dynadoc.Fname( 'session id' ) ]:
        ''' Create new HTTP session for API communication. '''
        pass

    def make_request(
        session_id: Annotated[ str, dynadoc.Fname( 'session id' ) ],
        endpoint: Annotated[ str, dynadoc.Doc( "API endpoint path" ) ],
        headers: Annotated[ dict, dynadoc.Fname( 'headers dict' ) ] = None,
        timeout: Annotated[ float, dynadoc.Fname( 'request timeout' ) ] = 60.0,
    ) -> Annotated[ dict, dynadoc.Fname( 'response data' ) ]:
        ''' Make HTTP request using existing session. '''
        pass

    # Apply documentation to all functions in the module
    dynadoc.assign_module_docstring( __name__, table = HTTP_FRAGMENTS )

This approach ensures consistent terminology across all HTTP-related
functions while making it easy to update descriptions in one place.


Class-Level Fragments
===============================================================================

Fragment tables can also be applied to classes, making them useful for
documenting related methods with shared concepts:

.. doctest:: Fragments

    >>> # Fragment table for data processing concepts
    >>> data_fragments = {
    ...     'input data': 'Raw input data to be processed',
    ...     'output format': 'Desired format for processed output',
    ...     'validation rules': 'Set of rules to validate data against',
    ...     'processed result': 'Data after processing and validation',
    ...     'error count': 'Number of validation errors encountered',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = data_fragments )
    ... class DataValidator:
    ...     ''' Data validation and processing utilities. '''
    ...
    ...     def validate(
    ...         self,
    ...         data: Annotated[ list, dynadoc.Fname( 'input data' ) ],
    ...         rules: Annotated[ dict, dynadoc.Fname( 'validation rules' ) ],
    ...     ) -> Annotated[ int, dynadoc.Fname( 'error count' ) ]:
    ...         ''' Validate input data against specified rules. '''
    ...         return 0
    ...
    ...     def process(
    ...         self,
    ...         data: Annotated[ list, dynadoc.Fname( 'input data' ) ],
    ...         format_spec: Annotated[ str, dynadoc.Fname( 'output format' ) ],
    ...     ) -> Annotated[ dict, dynadoc.Fname( 'processed result' ) ]:
    ...         ''' Process validated data into specified format. '''
    ...         return { }

.. code-block:: text

    >>> print( DataValidator.validate.__doc__ )
    Validate input data against specified rules.

    :argument data: Raw input data to be processed
    :type data: list
    :argument rules: Set of rules to validate data against
    :type rules: dict
    :returns: Number of validation errors encountered
    :rtype: int

.. code-block:: text

    >>> print( DataValidator.process.__doc__ )
    Process validated data into specified format.

    :argument data: Raw input data to be processed
    :type data: list
    :argument format_spec: Desired format for processed output
    :type format_spec: str
    :returns: Data after processing and validation
    :rtype: dict


Storing Fragments on Classes
===============================================================================

For complex classes with many methods sharing common concepts, you can store
fragments directly on the class using the ``_dynadoc_fragments_`` attribute.
This provides a way to include reusable documentation content in the class
itself:

.. doctest:: Fragments

    >>> # Fragment table for method parameters
    >>> config_fragments = {
    ...     'config_path': 'Path to configuration file',
    ...     'validation_strict': 'Whether to enforce strict validation rules',
    ...     'success_status': 'True if operation completed successfully',
    ...     'config_manager': 'Manages application configuration and settings',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = config_fragments )
    ... class ConfigurationManager:
    ...     ''' Application configuration management system. '''
    ...
    ...     # Store fragments directly on the class
    ...     _dynadoc_fragments_ = (
    ...         dynadoc.Doc( "Provides centralized configuration management" ),
    ...         "config_manager",  # Reference to external table
    ...         dynadoc.Doc( "Supports multiple configuration file formats" ),
    ...     )
    ...
    ...     def __init__( self ):
    ...         self._config = { }
    >>>
    >>> print( ConfigurationManager.__doc__ )
    Application configuration management system.
    <BLANKLINE>
    Provides centralized configuration management
    <BLANKLINE>
    Manages application configuration and settings
    <BLANKLINE>
    Supports multiple configuration file formats

The ``_dynadoc_fragments_`` attribute can contain:

- **Doc objects**: Inline documentation that gets included directly
- **String references**: Keys that get looked up in the fragment table

When a class is decorated, fragments from ``_dynadoc_fragments_`` are
automatically included in the class docstring, providing a way to share
common documentation across related classes.


Storing Fragments on Modules
===============================================================================

Similar to classes, modules can store fragments using the ``_dynadoc_fragments_``
attribute for module-level documentation that combines reusable content:

.. code-block:: python

    # data_processing.py
    ''' Data processing and transformation utilities. '''

    import dynadoc
    from typing import Annotated

    # Module-level fragments
    _dynadoc_fragments_ = (
        dynadoc.Doc( "High-performance data processing for large datasets" ),
        "processing_engine",  # Looked up from module fragment table
        dynadoc.Doc( "Supports multiple input and output formats" ),
    )

    # Module fragment table
    MODULE_FRAGMENTS = {
        'processing_engine': 'Built on optimized processing algorithms',
        'input_data': 'Raw data to be processed',
        'output_data': 'Processed and transformed data',
    }

    def transform_data(
        data: Annotated[ list, dynadoc.Fname( 'input_data' ) ]
    ) -> Annotated[ dict, dynadoc.Fname( 'output_data' ) ]:
        ''' Transform raw data into structured format. '''
        return { }

    # Apply documentation with fragments
    dynadoc.assign_module_docstring( __name__, table = MODULE_FRAGMENTS )

This pattern is particularly useful for packages where you want consistent
messaging about capabilities and features across module documentation.


Error Handling
===============================================================================

When a ``Fname`` references a key that doesn't exist in the fragment table,
``dynadoc`` will issue a warning but continue processing. This behavior is
customizable through the context's notifier function (see configuration
section for details):

.. doctest:: Fragments

    >>> # Fragment table missing some keys
    >>> incomplete_fragments = {
    ...     'valid key': 'This fragment exists',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = incomplete_fragments )
    ... def example_function(
    ...     param1: Annotated[ str, dynadoc.Fname( 'valid key' ) ],
    ...     param2: Annotated[ int, dynadoc.Fname( 'missing key' ) ],
    ... ) -> None:
    ...     ''' Example function with missing fragment reference. '''
    ...     pass
    ...
    >>> print( example_function.__doc__ )  # doctest: +ELLIPSIS
    Example function with missing fragment reference.
    <BLANKLINE>
    :argument param1: This fragment exists
    :type param1: str
    :argument param2:
    :type param2: int

The function with the valid fragment reference gets documented normally, while
the missing fragment results in an empty description (and a warning that would
appear in the console during processing).


Real-World Example: dynadoc Fragments
===============================================================================

The ``dynadoc`` library itself uses fragments extensively. You can examine the
fragment table defined in ``dynadoc/__/doctab.py``:

.. code-block:: python

    # From dynadoc/__/doctab.py
    fragments: _FragmentsTable = __.types.MappingProxyType( {
        'context': '''
            Data transfer object for various behaviors.

            Controls how annotations are resolved and how fragments are
            processed and rendered.
        ''',
        'fragment rectifier': ''' Cleans and normalizes documentation fragment. ''',
        'introspection': '''
            Controls on introspection behavior.

            Is introspection enabled?
            Which kinds of objects to recursively document?
            Etc...
        ''',
        'notifier': ''' Notifies of warnings and errors. ''',
        'renderer': ''' Produces docstring fragment from object and information about it. ''',
        # ... more fragments
    } )

These fragments are then used throughout the library's type annotations to
maintain consistent documentation. For example, in function signatures you'll
see annotations like:

.. code-block:: python

    context: Annotated[ Context, Fname( 'context' ) ]
    renderer: Annotated[ Renderer, Fname( 'renderer' ) ]

This ensures that parameter descriptions remain consistent across the entire
codebase and can be updated in a single location.


Fragment Best Practices
===============================================================================

When using fragments effectively:

**Create semantic fragment names** that clearly indicate their purpose::

    fragments = {
        'api key': 'Authentication key for API access',
        'request timeout': 'Request timeout in seconds',
        'base url': 'Base URL for API endpoints',
    }

**Group related fragments** by domain or module to keep them organized::

    # HTTP-related fragments
    http_fragments = { ... }

    # Data processing fragments
    data_fragments = { ... }

    # Configuration management fragments
    config_fragments = { ... }

**Prefer fragments for repeated concepts** while using ``Doc`` for specific,
one-off descriptions::

    # Good use of fragments
    timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ]

    # Good use of Doc for specific cases
    config_file: Annotated[ str, dynadoc.Doc( "Path to this specific config file" ) ]

**Use consistent terminology** across all fragments to maintain professional
documentation standards::

    # Consistent: always use "timeout" not "time limit" or "wait time"
    'request timeout': 'Maximum time to wait for request completion',
    'connection timeout': 'Maximum time to wait for connection establishment',

**Write clear fragment content** that provides useful information in
documentation contexts::

    # Good: provides meaningful context
    'api key': 'Authentication key for API access'

    # Too brief: not enough context
    'api key': 'API key'

    # Multi-line fragments are perfectly acceptable
    'context': '''
        Data transfer object for various behaviors.

        Controls how annotations are resolved and how fragments are
        processed and rendered.
    '''

**Leverage fragment storage on classes and modules** to create rich, reusable
documentation that can be shared across related functionality while maintaining
consistency and reducing duplication.

.. note::

   **Attribute Limitations**

   Some Python objects cannot have custom attributes added to them. For example,
   ``enum`` classes and certain built-in types do not support adding
   ``_dynadoc_fragments_`` attributes. This means they cannot use the convenient
   attribute-based fragment injection mechanism (neither ``Doc`` objects nor
   ``Fname`` references).

   For such objects, you have two options:

   - Decorate them separately with ``@with_docstring`` and pass fragments as
     arguments to the decorator
   - Use special introspectors (like ``dynadoc`` does for enum classes) that
     handle the documentation generation differently
