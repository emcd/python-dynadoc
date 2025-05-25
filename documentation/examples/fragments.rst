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
    >>> common_fragments = {
    ...     'user id': 'Unique identifier for a user account',
    ...     'timeout': 'Timeout duration in seconds',
    ...     'retry count': 'Number of retry attempts before giving up',
    ...     'success status': 'Whether the operation completed successfully',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = common_fragments )
    ... def create_user(
    ...     user_id: Annotated[ int, dynadoc.Fname( 'user id' ) ],
    ...     timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ] = 30.0,
    ... ) -> Annotated[ bool, dynadoc.Fname( 'success status' ) ]:
    ...     ''' Create a new user account. '''
    ...     return True
    ...
    >>> print( create_user.__doc__ )
    Create a new user account.
    <BLANKLINE>
    :argument user_id: Unique identifier for a user account
    :type user_id: int
    :argument timeout: Timeout duration in seconds
    :type timeout: float
    :returns: Whether the operation completed successfully
    :rtype: bool

Notice how ``Fname( 'user id' )`` references the ``'user id'`` key in the
fragment table, automatically substituting the full description.


Combining Doc and Fname
===============================================================================

You can mix ``Doc`` and ``Fname`` annotations in the same function, providing
flexibility for both specific and reusable descriptions:

.. doctest:: Fragments

    >>> @dynadoc.with_docstring( table = common_fragments )
    ... def retry_operation(
    ...     operation_name: Annotated[ str, dynadoc.Doc( "Name of the operation to retry" ) ],
    ...     max_retries: Annotated[ int, dynadoc.Fname( 'retry count' ) ],
    ...     timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ] = 60.0,
    ... ) -> Annotated[ bool, dynadoc.Fname( 'success status' ) ]:
    ...     ''' Retry a failed operation with configurable parameters. '''
    ...     return True
    ...
    >>> print( retry_operation.__doc__ )
    Retry a failed operation with configurable parameters.
    <BLANKLINE>
    :argument operation_name: Name of the operation to retry
    :type operation_name: str
    :argument max_retries: Number of retry attempts before giving up
    :type max_retries: int
    :argument timeout: Timeout duration in seconds
    :type timeout: float
    :returns: Whether the operation completed successfully
    :rtype: bool


Module-Level Fragments
===============================================================================

Fragment tables are particularly useful for module-level documentation where
multiple functions share common parameter patterns:

.. code-block:: python

    # database.py
    ''' Database connection and query utilities. '''

    import dynadoc
    from typing import Annotated

    # Define fragments for common database concepts
    DB_FRAGMENTS = {
        'connection string': 'Database connection string in URI format',
        'query timeout': 'Maximum time to wait for query completion in seconds',
        'transaction id': 'Unique identifier for the database transaction',
        'row count': 'Number of rows affected by the operation',
        'connection pool': 'Pool of reusable database connections',
    }

    def connect(
        connection_string: Annotated[ str, dynadoc.Fname( 'connection string' ) ],
        timeout: Annotated[ float, dynadoc.Fname( 'query timeout' ) ] = 30.0,
    ) -> Annotated[ object, dynadoc.Fname( 'connection pool' ) ]:
        ''' Establish connection to the database. '''
        pass

    def execute_query(
        query: Annotated[ str, dynadoc.Doc( "SQL query to execute" ) ],
        connection: Annotated[ object, dynadoc.Fname( 'connection pool' ) ],
        timeout: Annotated[ float, dynadoc.Fname( 'query timeout' ) ] = 60.0,
    ) -> Annotated[ int, dynadoc.Fname( 'row count' ) ]:
        ''' Execute a SQL query and return affected row count. '''
        pass

    # Apply documentation to all functions in the module
    dynadoc.assign_module_docstring( __name__, table = DB_FRAGMENTS )

This approach ensures consistent terminology across all database-related
functions while making it easy to update descriptions in one place.


Class-Level Fragments
===============================================================================

Fragment tables can also be applied to classes, making them useful for
documenting related methods with shared concepts:

.. doctest:: Fragments

    >>> # Fragment table for HTTP-related concepts
    >>> http_fragments = {
    ...     'http method': 'HTTP method (GET, POST, PUT, DELETE, etc.)',
    ...     'url path': 'URL path component for the API endpoint',
    ...     'request headers': 'Dictionary of HTTP headers to include',
    ...     'response data': 'Parsed response data from the server',
    ...     'status code': 'HTTP status code returned by the server',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = http_fragments )
    ... class APIClient:
    ...     ''' HTTP client for interacting with REST APIs. '''
    ...
    ...     def get(
    ...         self,
    ...         path: Annotated[ str, dynadoc.Fname( 'url path' ) ],
    ...         headers: Annotated[ dict, dynadoc.Fname( 'request headers' ) ] = None,
    ...     ) -> Annotated[ dict, dynadoc.Fname( 'response data' ) ]:
    ...         ''' Perform GET request to the specified path. '''
    ...         return { }
    ...
    ...     def post(
    ...         self,
    ...         path: Annotated[ str, dynadoc.Fname( 'url path' ) ],
    ...         data: Annotated[ dict, dynadoc.Doc( "Request payload data" ) ],
    ...         headers: Annotated[ dict, dynadoc.Fname( 'request headers' ) ] = None,
    ...     ) -> Annotated[ dict, dynadoc.Fname( 'response data' ) ]:
    ...         ''' Perform POST request with data payload. '''
    ...         return { }

.. code-block:: text

    >>> print( APIClient.get.__doc__ )
    Perform GET request to the specified path.

    :argument path: URL path component for the API endpoint
    :type path: str
    :argument headers: Dictionary of HTTP headers to include
    :type headers: dict
    :returns: Parsed response data from the server
    :rtype: dict

.. code-block:: text

    >>> print( APIClient.post.__doc__ )
    Perform POST request with data payload.

    :argument path: URL path component for the API endpoint
    :type path: str
    :argument data: Request payload data
    :type data: dict
    :argument headers: Dictionary of HTTP headers to include
    :type headers: dict
    :returns: Parsed response data from the server
    :rtype: dict


Storing Fragments on Classes
===============================================================================

For complex classes with many methods sharing common concepts, you can store
fragments directly on the class using the ``_dynadoc_fragments_`` attribute:

.. doctest:: Fragments

    >>> # Fragment table for method parameters
    >>> db_fragments = {
    ...     'database_host': 'Hostname or IP address of database server',
    ...     'timeout_seconds': 'Connection timeout in seconds',
    ...     'success_status': 'True if operation completed successfully',
    ...     'connection_pool': 'Maintains pool of reusable database connections',
    ... }
    >>>
    >>> @dynadoc.with_docstring( table = db_fragments )
    ... class DatabaseManager:
    ...     ''' Manages database connections and operations. '''
    ...
    ...     # Store fragments directly on the class
    ...     _dynadoc_fragments_ = (
    ...         dynadoc.Doc( "Database manager for handling connections" ),
    ...         "connection_pool",  # Reference to external table
    ...     )
    ...
    ...     def __init__( self ):
    ...         self._pool = None
    >>>
    >>> print( DatabaseManager.__doc__ )
    Manages database connections and operations.
    <BLANKLINE>
    Database manager for handling connections
    <BLANKLINE>
    Maintains pool of reusable database connections

The ``_dynadoc_fragments_`` attribute can contain:

- **Doc objects**: Inline documentation that gets included directly
- **String references**: Keys that get looked up in the fragment table

When a class is decorated, fragments from ``_dynadoc_fragments_`` are
automatically included in the class docstring, providing a way to share
common documentation across related classes.


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
        'user id': 'Unique identifier for a user account',
        'db timeout': 'Database operation timeout in seconds',
        'api key': 'Authentication key for API access',
    }

**Group related fragments** by domain or module to keep them organized::

    # HTTP-related fragments
    http_fragments = { ... }

    # Database-related fragments
    db_fragments = { ... }

    # Authentication-related fragments
    auth_fragments = { ... }

**Prefer fragments for repeated concepts** while using ``Doc`` for specific,
one-off descriptions::

    # Good use of fragments
    timeout: Annotated[ float, dynadoc.Fname( 'timeout' ) ]

    # Good use of Doc for specific cases
    config_file: Annotated[ str, dynadoc.Doc( "Path to this specific config file" ) ]

**Keep fragment text concise** but descriptive enough to be useful in
documentation contexts.

**Use consistent terminology** across all fragments to maintain professional
documentation standards.
