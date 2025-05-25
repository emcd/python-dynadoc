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
Classes
*******************************************************************************


Introduction
===============================================================================

The ``dynadoc`` library excels at documenting classes by automatically
processing type annotations on class attributes and method parameters. It can
distinguish between class variables, instance variables, and methods, producing
appropriate Sphinx-compatible documentation for each.

.. doctest:: Classes

    >>> import dynadoc
    >>> from typing import Annotated, ClassVar


Simple Class Documentation
===============================================================================

Class attributes with ``Doc`` annotations are automatically documented:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class APIEndpoint:
    ...     ''' Represents a REST API endpoint configuration. '''
    ...
    ...     url: Annotated[ str, dynadoc.Doc( "Full URL of the API endpoint" ) ]
    ...     method: Annotated[ str, dynadoc.Doc( "HTTP method (GET, POST, etc.)" ) ]
    ...
    ...     def __init__( self, url: str, method: str = "GET" ) -> None:
    ...         self.url = url
    ...         self.method = method
    ...
    >>> print( APIEndpoint.__doc__ )
    Represents a REST API endpoint configuration.
    <BLANKLINE>
    :ivar url: Full URL of the API endpoint
    :vartype url: str
    :ivar method: HTTP method (GET, POST, etc.)
    :vartype method: str


Class Variables versus Instance Variables
===============================================================================

The library distinguishes between class variables and instance variables using
``ClassVar`` annotations:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class HTTPClient:
    ...     ''' HTTP client with configurable defaults and per-instance settings. '''
    ...
    ...     default_timeout: Annotated[ ClassVar[ int ], dynadoc.Doc( "Default request timeout in seconds" ) ] = 30
    ...     max_retries: Annotated[ ClassVar[ int ], dynadoc.Doc( "Maximum retry attempts for failed requests" ) ] = 3
    ...
    ...     base_url: Annotated[ str, dynadoc.Doc( "Base URL for all requests from this client" ) ]
    ...     api_key: Annotated[ str, dynadoc.Doc( "Authentication key for API access" ) ]
    ...     timeout: Annotated[ int | None, dynadoc.Doc( "Request timeout override for this client" ) ] = None
    ...
    >>> print( HTTPClient.__doc__ )
    HTTP client with configurable defaults and per-instance settings.
    <BLANKLINE>
    :cvar default_timeout: Default request timeout in seconds
    :vartype default_timeout: typing.ClassVar[ int ]
    :cvar max_retries: Maximum retry attempts for failed requests
    :vartype max_retries: typing.ClassVar[ int ]
    :ivar base_url: Base URL for all requests from this client
    :vartype base_url: str
    :ivar api_key: Authentication key for API access
    :vartype api_key: str
    :ivar timeout: Request timeout override for this client
    :vartype timeout: int | None


Scanning Unannotated Attributes
===============================================================================

By default, ``dynadoc`` only documents attributes that have type annotations.
However, you can enable scanning of unannotated attributes using the
``scan_attributes`` option in class introspection control:

.. doctest:: Classes

    >>> # Configure introspection to scan unannotated attributes
    >>> scan_introspection = dynadoc.IntrospectionControl(
    ...     class_control = dynadoc.ClassIntrospectionControl(
    ...         scan_attributes = True
    ...     )
    ... )
    >>>
    >>> @dynadoc.with_docstring( introspection = scan_introspection )
    ... class DataProcessor:
    ...     ''' Processes data files with configurable settings. '''
    ...
    ...     # Annotated attributes (always documented)
    ...     input_format: Annotated[ str, dynadoc.Doc( "Expected input file format" ) ]
    ...     output_dir: str  # Type annotation but no Doc
    ...
    ...     # Unannotated attributes (only documented with scan_attributes=True)
    ...     default_encoding = "utf-8"
    ...     chunk_size = 1024
    ...     _debug_mode = False  # Private, won't be documented
    ...
    >>> print( DataProcessor.__doc__ )
    Processes data files with configurable settings.
    <BLANKLINE>
    :ivar input_format: Expected input file format
    :vartype input_format: str
    :ivar output_dir:
    :vartype output_dir: str
    :cvar chunk_size:
    :cvar default_encoding:

Notice that:

- ``input_format`` appears with its description from the ``Doc`` annotation
- ``output_dir`` appears with type information but no description
- ``chunk_size`` and ``default_encoding`` appear without type information
- ``_debug_mode`` is hidden due to the underscore prefix

The ``scan_attributes`` feature is particularly useful for documenting classes
that mix modern type annotations with legacy code or when you want to document
important constants that don't need type annotations.


Method Documentation
===============================================================================

Methods within classes are **not** automatically documented by default. The
``@with_docstring`` decorator only processes the target object itself (in this
case, the class and its attributes):

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class FileValidator:
    ...     ''' Validates file content and format. '''
    ...
    ...     def validate_format(
    ...         self,
    ...         filepath: Annotated[ str, dynadoc.Doc( "Path to file to validate" ) ],
    ...         expected_format: Annotated[ str, dynadoc.Doc( "Expected file format" ) ],
    ...     ) -> Annotated[ bool, dynadoc.Doc( "True if file format is valid" ) ]:
    ...         ''' Validate that file matches expected format. '''
    ...         return True
    ...
    >>> FileValidator.__doc__
    'Validates file content and format.'
    >>> FileValidator.validate_format.__doc__.strip()  # No automatic documentation
    'Validate that file matches expected format.'

To document individual methods, you must either decorate them separately or
enable introspection on the class:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class ConfigManager:
    ...     ''' Manages application configuration settings. '''
    ...
    ...     @dynadoc.with_docstring( )
    ...     def load_config(
    ...         self,
    ...         config_path: Annotated[ str, dynadoc.Doc( "Path to configuration file" ) ],
    ...         validate: Annotated[ bool, dynadoc.Doc( "Whether to validate config" ) ] = True,
    ...     ) -> Annotated[ dict, dynadoc.Doc( "Loaded configuration data" ) ]:
    ...         ''' Load configuration from file. '''
    ...         return { }
    ...
    ...     @dynadoc.with_docstring( )
    ...     def save_config(
    ...         self,
    ...         config_data: Annotated[ dict, dynadoc.Doc( "Configuration data to save" ) ],
    ...         output_path: Annotated[ str, dynadoc.Doc( "Path where config will be saved" ) ],
    ...     ) -> Annotated[
    ...         None,
    ...         dynadoc.Raises( OSError, "When file cannot be written" ),
    ...         dynadoc.Raises( ValueError, "When config data is invalid" ),
    ...     ]:
    ...         ''' Save configuration data to file. '''
    ...         pass
    ...
    >>> print( ConfigManager.load_config.__doc__ )
    Load configuration from file.
    <BLANKLINE>
    :argument self:
    :argument config_path: Path to configuration file
    :type config_path: str
    :argument validate: Whether to validate config
    :type validate: bool
    :returns: Loaded configuration data
    :rtype: dict

    >>> print( ConfigManager.save_config.__doc__ )
    Save configuration data to file.
    <BLANKLINE>
    :argument self:
    :argument config_data: Configuration data to save
    :type config_data: dict
    :argument output_path: Path where config will be saved
    :type output_path: str
    <BLANKLINE>
    :raises OSError: When file cannot be written
    :raises ValueError: When config data is invalid


Recursive Documentation with Introspection
===============================================================================

For automatic documentation of all methods in a class, you need to enable
introspection by creating an ``IntrospectionControl`` object:

.. doctest:: Classes

    >>> introspection = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargets.Function
    ... )

and applying a decorator with it:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( introspection = introspection )
    ... class DataTransformer:
    ...     ''' Collection of data transformation utilities. '''
    ...
    ...     @staticmethod
    ...     def normalize_text(
    ...         text: Annotated[ str, dynadoc.Doc( "Text to normalize" ) ]
    ...     ) -> Annotated[ str, dynadoc.Doc( "Normalized text output" ) ]:
    ...         return text.strip( ).lower( )
    ...
    ...     @staticmethod
    ...     def parse_csv_line(
    ...         line: Annotated[ str, dynadoc.Doc( "CSV line to parse" ) ]
    ...     ) -> Annotated[ list[ str ], dynadoc.Doc( "Parsed field values" ) ]:
    ...         return line.split( ',' )
    ...

The class docstring remains unchanged, but now the individual methods are
automatically documented:

.. code-block:: text

    >>> print( DataTransformer.__doc__ )
    Collection of data transformation utilities.

.. code-block:: text

    >>> print( DataTransformer.normalize_text.__doc__ )
    :argument text: Text to normalize
    :type text: str
    :returns: Normalized text output
    :rtype: str

.. code-block:: text

    >>> print( DataTransformer.parse_csv_line.__doc__ )
    :argument line: CSV line to parse
    :type line: str
    :returns: Parsed field values
    :rtype: list[ str ]


Property Documentation
===============================================================================

Properties require enabling descriptor introspection to be automatically
documented. Like methods, they are not processed by default:

.. doctest:: Classes

    >>> descriptor_introspection = dynadoc.IntrospectionControl(
    ...     targets = dynadoc.IntrospectionTargets.Descriptor
    ... )
    >>>
    >>> @dynadoc.with_docstring( introspection = descriptor_introspection )
    ... class DatabaseConnection:
    ...     ''' Database connection with status monitoring. '''
    ...
    ...     def __init__( self, connection_string: str ):
    ...         self._connection_string = connection_string
    ...         self._is_connected = False
    ...
    ...     @property
    ...     def status( self ) -> Annotated[
    ...         str,
    ...         dynadoc.Doc( "Current connection status" ),
    ...         dynadoc.Raises( ConnectionError, "If connection state is invalid" )
    ...     ]:
    ...         ''' Connection status property. '''
    ...         if not hasattr( self, '_is_connected' ):
    ...             raise ConnectionError( "Connection state not initialized" )
    ...         return "connected" if self._is_connected else "disconnected"
    ...
    ...     @property
    ...     def connection_info( self ) -> Annotated[ dict, dynadoc.Doc( "Connection metadata" ) ]:
    ...         ''' Connection information. '''
    ...         return { "status": self.status, "string": self._connection_string }

When properties are introspected, ``dynadoc`` automatically processes the
property's getter method to extract documentation from its type annotations.
The generated documentation appears on the property itself:

.. code-block:: text

    >>> print( DatabaseConnection.status.__doc__ )
    Connection status property.

    :returns: Current connection status
    :rtype: str
    :raises ConnectionError: If connection state is invalid

.. code-block:: text

    >>> print( DatabaseConnection.connection_info.__doc__ )
    Connection information.

    :returns: Connection metadata
    :rtype: dict

This approach allows properties to have rich documentation including exception
information, which is particularly useful for properties that perform validation
or can fail under certain conditions.


Fragment Integration
===============================================================================

Classes work seamlessly with the fragment system for reusable documentation.
For detailed information about using fragments with classes, including storing
fragments directly on classes with ``_dynadoc_fragments_``, see the
:doc:`fragments` section.
