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
Basic Usage
*******************************************************************************


Introduction
===============================================================================

While Sphinx Autodoc can process simple type annotations, it falls down when
encountering ``Annotated`` types with rich metadata. The ``dynadoc`` library
bridges this gap by extracting documentation from :pep:`727` ``Doc`` objects,
``Raises`` specifications, and other annotation metadata to generate
comprehensive docstrings.

.. doctest:: Basic.Usage

    >>> import dynadoc
    >>> from typing import Annotated


Simple Function Documentation
===============================================================================

The most basic use case is decorating a function with type annotations that
include ``Doc`` objects:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def validate_api_response(
    ...     response_data: Annotated[ dict, dynadoc.Doc( "Raw API response data" ) ],
    ...     schema_name: Annotated[ str, dynadoc.Doc( "Name of validation schema to use" ) ],
    ...     strict_mode: Annotated[ bool, dynadoc.Doc( "Whether to enforce strict validation" ) ],
    ...     timeout: Annotated[ float, dynadoc.Doc( "Validation timeout in seconds" ) ],
    ... ) -> Annotated[ bool, dynadoc.Doc( "True if response is valid" ) ]:
    ...     ''' Validate API response data against specified schema. '''
    ...     return True
    ...
    >>> print( validate_api_response.__doc__ )
    Validate API response data against specified schema.
    <BLANKLINE>
    :argument response_data: Raw API response data
    :type response_data: dict
    :argument schema_name: Name of validation schema to use
    :type schema_name: str
    :argument strict_mode: Whether to enforce strict validation
    :type strict_mode: bool
    :argument timeout: Validation timeout in seconds
    :type timeout: float
    :returns: True if response is valid
    :rtype: bool


Exception Documentation
===============================================================================

Functions that raise exceptions can document them using ``Raises`` annotations:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def parse_config_file(
    ...     filepath: Annotated[ str, dynadoc.Doc( "Path to configuration file" ) ],
    ...     encoding: Annotated[ str, dynadoc.Doc( "File encoding to use" ) ] = "utf-8",
    ... ) -> Annotated[
    ...     dict,
    ...     dynadoc.Doc( "Parsed configuration data" ),
    ...     dynadoc.Raises( FileNotFoundError, "When config file does not exist" ),
    ...     dynadoc.Raises( ValueError, "When file contains invalid JSON/YAML" ),
    ... ]:
    ...     if not filepath.endswith( ( '.json', '.yaml', '.yml' ) ):
    ...         raise ValueError( "Unsupported file format" )
    ...     return { }
    ...
    >>> print( parse_config_file.__doc__ )
    :argument filepath: Path to configuration file
    :type filepath: str
    :argument encoding: File encoding to use
    :type encoding: str
    :returns: Parsed configuration data
    :rtype: dict
    :raises FileNotFoundError: When config file does not exist
    :raises ValueError: When file contains invalid JSON/YAML


Multiple Exception Types
===============================================================================

When a function can raise multiple exception types for the same condition, you
can specify them as a sequence in a single ``Raises`` annotation. This allows
multiple exceptions to share the same description:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def download_file(
    ...     url: Annotated[ str, dynadoc.Doc( "URL of file to download" ) ],
    ...     output_path: Annotated[ str, dynadoc.Doc( "Local path to save file" ) ]
    ... ) -> Annotated[
    ...     int,
    ...     dynadoc.Doc( "Number of bytes downloaded" ),
    ...     dynadoc.Raises(
    ...         [ ConnectionError, TimeoutError ],
    ...         "When network connection fails"
    ...     ),
    ...     dynadoc.Raises(
    ...         [ PermissionError, OSError ],
    ...         "When file cannot be saved to output path"
    ...     ),
    ... ]:
    ...     ''' Download file from URL to local filesystem. '''
    ...     return 0
    ...
    >>> print( download_file.__doc__ )
    Download file from URL to local filesystem.
    <BLANKLINE>
    :argument url: URL of file to download
    :type url: str
    :argument output_path: Local path to save file
    :type output_path: str
    :returns: Number of bytes downloaded
    :rtype: int
    :raises ConnectionError: When network connection fails
    :raises TimeoutError: When network connection fails
    :raises PermissionError: When file cannot be saved to output path
    :raises OSError: When file cannot be saved to output path

Notice how each exception type in the sequence gets its own ``:raises:`` line
with the same description, allowing comprehensive documentation of all possible
exception scenarios.


Preserving Existing Docstrings
===============================================================================

By default, ``dynadoc`` preserves any existing docstring content and appends
the generated documentation:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def transform_data(
    ...     raw_data: Annotated[ list[ dict ], dynadoc.Doc( "Input data records" ) ],
    ...     normalize: Annotated[ bool, dynadoc.Doc( "Whether to normalize values" ) ] = True,
    ... ) -> Annotated[ list[ dict ], dynadoc.Doc( "Transformed data records" ) ]:
    ...     ''' Transform raw data records with optional normalization.
    ...
    ...         This function demonstrates how dynadoc preserves existing
    ...         docstring content while adding parameter documentation.
    ...
    ...         The transformation includes data cleaning, type conversion,
    ...         and optional value normalization.
    ...     '''
    ...     result = [ { k: str( v ).strip( ) for k, v in record.items( ) } for record in raw_data ]
    ...     if normalize:
    ...         result = [ { k: v.lower( ) if isinstance( v, str ) else v for k, v in record.items( ) } for record in result ]
    ...     return result
    ...
    >>> print( transform_data.__doc__ )
    Transform raw data records with optional normalization.
    <BLANKLINE>
    This function demonstrates how dynadoc preserves existing
    docstring content while adding parameter documentation.
    <BLANKLINE>
    The transformation includes data cleaning, type conversion,
    and optional value normalization.
    <BLANKLINE>
    :argument raw_data: Input data records
    :type raw_data: list[ dict ]
    :argument normalize: Whether to normalize values
    :type normalize: bool
    :returns: Transformed data records
    :rtype: list[ dict ]

To replace existing docstrings instead of preserving them, use ``preserve = False``:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( preserve = False )
    ... def calculate_checksum(
    ...     data: Annotated[ bytes, dynadoc.Doc( "Data to checksum" ) ],
    ...     algorithm: Annotated[ str, dynadoc.Doc( "Hash algorithm to use" ) ] = "sha256",
    ... ) -> Annotated[ str, dynadoc.Doc( "Hexadecimal checksum string" ) ]:
    ...     ''' This docstring will be replaced. '''
    ...     return "abc123"
    ...
    >>> print( calculate_checksum.__doc__ )
    :argument data: Data to checksum
    :type data: bytes
    :argument algorithm: Hash algorithm to use
    :type algorithm: str
    :returns: Hexadecimal checksum string
    :rtype: str


Optional Parameters and Defaults
===============================================================================

The library handles optional parameters and default values appropriately:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def create_api_client(
    ...     base_url: Annotated[ str, dynadoc.Doc( "Base URL for API requests" ) ],
    ...     api_key: Annotated[ str, dynadoc.Doc( "Authentication API key" ) ],
    ...     timeout: Annotated[ int | None, dynadoc.Doc( "Request timeout in seconds" ) ] = None,
    ...     verify_ssl: Annotated[ bool, dynadoc.Doc( "Whether to verify SSL certificates" ) ] = True,
    ... ) -> Annotated[ dict, dynadoc.Doc( "Configured API client instance" ) ]:
    ...     client_config = { "base_url": base_url, "api_key": api_key, "verify_ssl": verify_ssl }
    ...     if timeout is not None:
    ...         client_config[ "timeout" ] = timeout
    ...     return client_config
    ...
    >>> print( create_api_client.__doc__ )
    :argument base_url: Base URL for API requests
    :type base_url: str
    :argument api_key: Authentication API key
    :type api_key: str
    :argument timeout: Request timeout in seconds
    :type timeout: int | None
    :argument verify_ssl: Whether to verify SSL certificates
    :type verify_ssl: bool
    :returns: Configured API client instance
    :rtype: dict


Rendering Styles
===============================================================================

The default renderer produces Sphinx-compatible reStructuredText with legible
spacing. For more compact output following PEP 8 style guidelines:

.. doctest:: Basic.Usage

    >>> from dynadoc.renderers import sphinxad
    >>> def compact_renderer( obj, info, context ):
    ...     return sphinxad.produce_fragment( obj, info, context, style = sphinxad.Style.Pep8 )
    >>>
    >>> @dynadoc.with_docstring( renderer = compact_renderer )
    ... def process_metadata(
    ...     data_map: Annotated[ dict[ str, list[ int ] ], dynadoc.Doc( "Mapping of identifiers to value lists" ) ],
    ... ) -> Annotated[ dict[ str, int ], dynadoc.Doc( "Processed summary data" ) ]:
    ...     return { k: sum( v ) for k, v in data_map.items( ) }
    ...
    >>> print( process_metadata.__doc__ )
    :argument data_map: Mapping of identifiers to value lists
    :type data_map: dict[str, list[int]]
    :returns: Processed summary data
    :rtype: dict[str, int]

Compare this compact PEP 8 style (``dict[str, list[int]]``) with the default
legible style (``dict[ str, list[ int ] ]``) used in all previous examples.
The difference is most apparent with complex generic types.
