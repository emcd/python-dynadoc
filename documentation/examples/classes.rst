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
    ... class Point2D:
    ...     ''' A point in 2D coordinate space. '''
    ...
    ...     x: Annotated[ float, dynadoc.Doc( "X coordinate of the point" ) ]
    ...     y: Annotated[ float, dynadoc.Doc( "Y coordinate of the point" ) ]
    ...
    ...     def __init__( self, x: float, y: float ) -> None:
    ...         self.x = x
    ...         self.y = y
    ...
    >>> print( Point2D.__doc__ )
    A point in 2D coordinate space.
    <BLANKLINE>
    :ivar x: X coordinate of the point
    :vartype x: float
    :ivar y: Y coordinate of the point
    :vartype y: float


Class Variables versus Instance Variables
===============================================================================

The library distinguishes between class variables and instance variables using
``ClassVar`` annotations:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class Species:
    ...     ''' Represents a biological species. '''
    ...
    ...     kingdom: Annotated[ ClassVar[ str ], dynadoc.Doc( "Taxonomic kingdom" ) ] = "Animalia"
    ...     phylum: Annotated[ ClassVar[ str ], dynadoc.Doc( "Taxonomic phylum" ) ] = "Chordata"
    ...
    ...     common_name: Annotated[ str, dynadoc.Doc( "Common name of the species" ) ]
    ...     scientific_name: Annotated[ str, dynadoc.Doc( "Binomial scientific name" ) ]
    ...     population: Annotated[ int | None, dynadoc.Doc( "Estimated population count" ) ] = None
    ...
    >>> print( Species.__doc__ )
    Represents a biological species.
    <BLANKLINE>
    :cvar kingdom: Taxonomic kingdom
    :vartype kingdom: typing.ClassVar[ str ]
    :cvar phylum: Taxonomic phylum
    :vartype phylum: typing.ClassVar[ str ]
    :ivar common_name: Common name of the species
    :vartype common_name: str
    :ivar scientific_name: Binomial scientific name
    :vartype scientific_name: str
    :ivar population: Estimated population count
    :vartype population: int | None


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
    ... class MixedClass:
    ...     ''' Class with both annotated and unannotated attributes. '''
    ...
    ...     # Annotated attributes (always documented)
    ...     annotated_attr: Annotated[ str, dynadoc.Doc( "This has documentation" ) ]
    ...     typed_attr: int  # Type annotation but no Doc
    ...
    ...     # Unannotated attributes (only documented with scan_attributes=True)
    ...     class_constant = "CONSTANT_VALUE"
    ...     default_timeout = 30
    ...     _private_setting = "hidden"  # Private, won't be documented
    ...
    >>> print( MixedClass.__doc__ )
    Class with both annotated and unannotated attributes.
    <BLANKLINE>
    :ivar annotated_attr: This has documentation
    :vartype annotated_attr: str
    :ivar typed_attr:
    :vartype typed_attr: int
    :cvar class_constant:
    :cvar default_timeout:

Notice that:

- ``annotated_attr`` appears with its description from the ``Doc`` annotation
- ``typed_attr`` appears with type information but no description
- ``class_constant`` and ``default_timeout`` appear without type information
- ``_private_setting`` is hidden due to the underscore prefix

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
    ... class Calculator:
    ...     ''' A simple calculator with basic operations. '''
    ...
    ...     def add(
    ...         self,
    ...         a: Annotated[ float, dynadoc.Doc( "First operand" ) ],
    ...         b: Annotated[ float, dynadoc.Doc( "Second operand" ) ],
    ...     ) -> Annotated[ float, dynadoc.Doc( "Sum of the operands" ) ]:
    ...         ''' Add two numbers together. '''
    ...         return a + b
    ...
    >>> Calculator.__doc__
    'A simple calculator with basic operations.'
    >>> Calculator.add.__doc__  # No automatic documentation
    ' Add two numbers together. '

To document individual methods, you must either decorate them separately or
enable introspection on the class:

.. doctest:: Classes

    >>> @dynadoc.with_docstring( )
    ... class Calculator:
    ...     ''' A simple calculator with basic operations. '''
    ...
    ...     @dynadoc.with_docstring( )
    ...     def add(
    ...         self,
    ...         a: Annotated[ float, dynadoc.Doc( "First operand" ) ],
    ...         b: Annotated[ float, dynadoc.Doc( "Second operand" ) ],
    ...     ) -> Annotated[ float, dynadoc.Doc( "Sum of the operands" ) ]:
    ...         ''' Add two numbers together. '''
    ...         return a + b
    ...
    ...     @dynadoc.with_docstring( )
    ...     def divide(
    ...         self,
    ...         dividend: Annotated[ float, dynadoc.Doc( "The number to be divided" ) ],
    ...         divisor: Annotated[ float, dynadoc.Doc( "The number to divide by" ) ],
    ...     ) -> Annotated[
    ...         float,
    ...         dynadoc.Doc( "The quotient" ),
    ...         dynadoc.Raises( ZeroDivisionError, "When divisor is zero" ),
    ...     ]:
    ...         ''' Divide one number by another. '''
    ...         if divisor == 0:
    ...             raise ZeroDivisionError( "Cannot divide by zero" )
    ...         return dividend / divisor
    ...
    >>> print( Calculator.add.__doc__ )
    Add two numbers together.
    <BLANKLINE>
    :argument self:
    :argument a: First operand
    :type a: float
    :argument b: Second operand
    :type b: float
    :returns: Sum of the operands
    :rtype: float

    >>> print( Calculator.divide.__doc__ )
    Divide one number by another.
    <BLANKLINE>
    :argument self:
    :argument dividend: The number to be divided
    :type dividend: float
    :argument divisor: The number to divide by
    :type divisor: float
    :returns: The quotient
    :rtype: float
    :raises ZeroDivisionError: When divisor is zero


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
    ... class MathUtils:
    ...     ''' Collection of mathematical utility functions. '''
    ...
    ...     @staticmethod
    ...     def square(
    ...         value: Annotated[ float, dynadoc.Doc( "Number to square" ) ]
    ...     ) -> Annotated[ float, dynadoc.Doc( "Square of the input" ) ]:
    ...         return value ** 2
    ...
    ...     @staticmethod
    ...     def cube(
    ...         value: Annotated[ float, dynadoc.Doc( "Number to cube" ) ]
    ...     ) -> Annotated[ float, dynadoc.Doc( "Cube of the input" ) ]:
    ...         return value ** 3
    ...

The class docstring remains unchanged, but now the individual methods are
automatically documented:

.. code-block:: text

    >>> print( MathUtils.__doc__ )
    Collection of mathematical utility functions.

.. code-block:: text

    >>> print( MathUtils.square.__doc__ )
    :argument value: Number to square
    :type value: float
    :returns: Square of the input
    :rtype: float

.. code-block:: text

    >>> print( MathUtils.cube.__doc__ )
    :argument value: Number to cube
    :type value: float
    :returns: Cube of the input
    :rtype: float


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
    ... class BankAccount:
    ...     ''' A bank account with balance management. '''
    ...
    ...     def __init__( self, initial_balance: float = 0.0 ):
    ...         self._balance = initial_balance
    ...         self._is_frozen = False
    ...
    ...     @property
    ...     def balance( self ) -> Annotated[
    ...         float,
    ...         dynadoc.Doc( "Current account balance in dollars" ),
    ...         dynadoc.Raises( ValueError, "If account data is corrupted" )
    ...     ]:
    ...         ''' Current account balance. '''
    ...         if self._balance < 0 and not hasattr( self, '_overdraft_allowed' ):
    ...             raise ValueError( "Account balance is negative without overdraft" )
    ...         return self._balance
    ...
    ...     @property
    ...     def is_active( self ) -> Annotated[ bool, dynadoc.Doc( "Whether account is active" ) ]:
    ...         ''' Account active status. '''
    ...         return not self._is_frozen

When properties are introspected, ``dynadoc`` automatically processes the
property's getter method to extract documentation from its type annotations.
The generated documentation appears on the property itself:

.. code-block:: text

    >>> print( BankAccount.balance.__doc__ )
    Current account balance.

    :returns: Current account balance in dollars
    :rtype: float
    :raises ValueError: If account data is corrupted

.. code-block:: text

    >>> print( BankAccount.is_active.__doc__ )
    Account active status.

    :returns: Whether account is active
    :rtype: bool

This approach allows properties to have rich documentation including exception
information, which is particularly useful for properties that perform validation
or can fail under certain conditions.
