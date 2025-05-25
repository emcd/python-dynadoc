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
    ... def calculate_distance(
    ...     x1: Annotated[ float, dynadoc.Doc( "X coordinate of first point" ) ],
    ...     y1: Annotated[ float, dynadoc.Doc( "Y coordinate of first point" ) ],
    ...     x2: Annotated[ float, dynadoc.Doc( "X coordinate of second point" ) ],
    ...     y2: Annotated[ float, dynadoc.Doc( "Y coordinate of second point" ) ],
    ... ) -> Annotated[ float, dynadoc.Doc( "Euclidean distance between the points" ) ]:
    ...     ''' Calculate the Euclidean distance between two points in 2D space. '''
    ...     return ( ( x2 - x1 ) ** 2 + ( y2 - y1 ) ** 2 ) ** 0.5
    ...
    >>> print( calculate_distance.__doc__ )
    Calculate the Euclidean distance between two points in 2D space.
    <BLANKLINE>
    :argument x1: X coordinate of first point
    :type x1: float
    :argument y1: Y coordinate of first point
    :type y1: float
    :argument x2: X coordinate of second point
    :type x2: float
    :argument y2: Y coordinate of second point
    :type y2: float
    :returns: Euclidean distance between the points
    :rtype: float


Exception Documentation
===============================================================================

Functions that raise exceptions can document them using ``Raises`` annotations:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def safe_divide(
    ...     numerator: Annotated[ float, dynadoc.Doc( "The dividend" ) ],
    ...     denominator: Annotated[ float, dynadoc.Doc( "The divisor" ) ],
    ... ) -> Annotated[
    ...     float,
    ...     dynadoc.Doc( "The quotient" ),
    ...     dynadoc.Raises( ZeroDivisionError, "When denominator is zero" ),
    ...     dynadoc.Raises( TypeError, "When inputs are not numeric" ),
    ... ]:
    ...     if not isinstance( numerator, ( int, float ) ):
    ...         raise TypeError( "Numerator must be numeric" )
    ...     if not isinstance( denominator, ( int, float ) ):
    ...         raise TypeError( "Denominator must be numeric" )
    ...     if denominator == 0:
    ...         raise ZeroDivisionError( "Cannot divide by zero" )
    ...     return numerator / denominator
    ...
    >>> print( safe_divide.__doc__ )
    :argument numerator: The dividend
    :type numerator: float
    :argument denominator: The divisor
    :type denominator: float
    :returns: The quotient
    :rtype: float
    :raises ZeroDivisionError: When denominator is zero
    :raises TypeError: When inputs are not numeric


Multiple Exception Types
===============================================================================

When a function can raise multiple exception types for the same condition, you
can specify them as a sequence in a single ``Raises`` annotation:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def parse_config_file(
    ...     filename: Annotated[ str, dynadoc.Doc( "Path to configuration file" ) ]
    ... ) -> Annotated[
    ...     dict,
    ...     dynadoc.Doc( "Parsed configuration data" ),
    ...     dynadoc.Raises(
    ...         ( FileNotFoundError, PermissionError ),
    ...         "When file cannot be accessed"
    ...     ),
    ...     dynadoc.Raises(
    ...         ( ValueError, KeyError ),
    ...         "When file contains invalid configuration data"
    ...     ),
    ... ]:
    ...     ''' Parse configuration from a JSON or YAML file. '''
    ...     # Implementation would go here
    ...     return { }
    ...
    >>> print( parse_config_file.__doc__ )
    Parse configuration from a JSON or YAML file.
    <BLANKLINE>
    :argument filename: Path to configuration file
    :type filename: str
    :returns: Parsed configuration data
    :rtype: dict
    :raises FileNotFoundError: When file cannot be accessed
    :raises PermissionError: When file cannot be accessed
    :raises ValueError: When file contains invalid configuration data
    :raises KeyError: When file contains invalid configuration data

Notice how each exception type in the sequence gets its own ``:raises:`` line
with the same description, allowing comprehensive documentation of all possible
exception scenarios.


Preserving Existing Docstrings
===============================================================================

By default, ``dynadoc`` preserves any existing docstring content and appends
the generated documentation:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def process_data(
    ...     data: Annotated[ list[ str ], dynadoc.Doc( "Input data to process" ) ],
    ...     normalize: Annotated[ bool, dynadoc.Doc( "Whether to normalize output" ) ] = True,
    ... ) -> Annotated[ list[ str ], dynadoc.Doc( "Processed data" ) ]:
    ...     ''' Process a list of strings with optional normalization.
    ...
    ...         This function demonstrates how dynadoc preserves existing
    ...         docstring content while adding parameter documentation.
    ...     '''
    ...     result = [ item.strip( ) for item in data ]
    ...     if normalize:
    ...         result = [ item.lower( ) for item in result ]
    ...     return result
    ...
    >>> print( process_data.__doc__ )
    Process a list of strings with optional normalization.
    <BLANKLINE>
    This function demonstrates how dynadoc preserves existing
    docstring content while adding parameter documentation.
    <BLANKLINE>
    :argument data: Input data to process
    :type data: list[ str ]
    :argument normalize: Whether to normalize output
    :type normalize: bool
    :returns: Processed data
    :rtype: list[ str ]

To replace existing docstrings instead of preserving them, use ``preserve = False``:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( preserve = False )
    ... def multiply(
    ...     a: Annotated[ float, dynadoc.Doc( "First number" ) ],
    ...     b: Annotated[ float, dynadoc.Doc( "Second number" ) ],
    ... ) -> Annotated[ float, dynadoc.Doc( "Product of the numbers" ) ]:
    ...     ''' This docstring will be replaced. '''
    ...     return a * b
    ...
    >>> print( multiply.__doc__ )
    :argument a: First number
    :type a: float
    :argument b: Second number
    :type b: float
    :returns: Product of the numbers
    :rtype: float


Optional Parameters and Defaults
===============================================================================

The library handles optional parameters and default values appropriately:

.. doctest:: Basic.Usage

    >>> @dynadoc.with_docstring( )
    ... def create_user(
    ...     name: Annotated[ str, dynadoc.Doc( "User's full name" ) ],
    ...     email: Annotated[ str, dynadoc.Doc( "User's email address" ) ],
    ...     age: Annotated[ int | None, dynadoc.Doc( "User's age in years" ) ] = None,
    ...     active: Annotated[ bool, dynadoc.Doc( "Whether user account is active" ) ] = True,
    ... ) -> Annotated[ dict[ str, any ], dynadoc.Doc( "User record dictionary" ) ]:
    ...     user = { "name": name, "email": email, "active": active }
    ...     if age is not None:
    ...         user[ "age" ] = age
    ...     return user
    ...
    >>> print( create_user.__doc__ )
    :argument name: User's full name
    :type name: str
    :argument email: User's email address
    :type email: str
    :argument age: User's age in years
    :type age: int | None
    :argument active: Whether user account is active
    :type active: bool
    :returns: User record dictionary
    :rtype: dict[ str, any ]


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
    ... def compact_example(
    ...     values: Annotated[ list[ int ], dynadoc.Doc( "List of integers" ) ],
    ... ) -> Annotated[ int, dynadoc.Doc( "Sum of all values" ) ]:
    ...     return sum( values )
    ...
    >>> print( compact_example.__doc__ )
    :argument values: List of integers
    :type values: list[int]
    :returns: Sum of all values
    :rtype: int
