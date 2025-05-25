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
Modules
*******************************************************************************


Introduction
===============================================================================

The ``dynadoc`` library provides ``assign_module_docstring`` for documenting
entire modules, including their annotated attributes and exported functions.
This is particularly useful for package ``__init__.py`` files and modules with
significant module-level annotations.

.. doctest:: Modules

    >>> import dynadoc
    >>> from typing import Annotated, TypeAlias


Basic Module Documentation
===============================================================================

Module-level annotations are documented by calling ``assign_module_docstring``
with the current module. You can pass either the module name as a string or
the actual module object:

.. code-block:: python

    # config.py
    ''' Application configuration module. '''

    import dynadoc
    from typing import Annotated

    # Module-level configuration with documented annotations
    version: Annotated[ str, dynadoc.Doc( "Version string of the application" ) ] = "1.0.0"
    debug_mode: Annotated[ bool, dynadoc.Doc( "Whether debug mode is enabled" ) ] = False
    max_connections: Annotated[ int, dynadoc.Doc( "Maximum allowed connections" ) ] = 100

    # Generate documentation using module name (most common)
    dynadoc.assign_module_docstring( __name__ )

    # Alternative: pass the actual module object
    import sys
    dynadoc.assign_module_docstring( sys.modules[ __name__ ] )

Both approaches produce the same result. Using the module name (``__name__``) is
more common and readable, while passing the module object directly can be useful
when you have a reference to a module from elsewhere.

After processing, the module's docstring would become:

.. code-block:: text

    Application configuration module.

    .. py:data:: version
        :type: str
        :value: '1.0.0'

    .. py:data:: debug_mode
        :type: bool
        :value: False

    .. py:data:: max_connections
        :type: int
        :value: 100

.. note::

    Due to current limitations in Sphinx, the ``.. py:data::`` directive does
    not support injecting custom descriptions from annotations. The descriptions
    are preserved in the source code for documentation purposes, but they do
    not appear in the rendered output. This limitation does not affect type
    aliases, which use ``.. py:type::`` and properly display descriptions.


TypeAlias Documentation
===============================================================================

Modules frequently define type aliases that benefit from rich documentation:

.. code-block:: python

    # types.py
    ''' Common type definitions for the application. '''

    import dynadoc
    from typing import Annotated, TypeAlias

    # Type aliases with comprehensive documentation
    UserId: Annotated[ TypeAlias, dynadoc.Doc( "Unique identifier for a user account" ) ] = int
    ConnectionPool: Annotated[ TypeAlias, dynadoc.Doc( "Pool of database connections" ) ] = list[ object ]
    ConfigDict: Annotated[ TypeAlias, dynadoc.Doc( "Configuration dictionary mapping strings to values" ) ] = dict[ str, str | int | bool ]

    dynadoc.assign_module_docstring( __name__ )

This generates clean documentation for the type aliases:

.. code-block:: text

    Common type definitions for the application.

    .. py:type:: UserId
        :canonical: int

        Unique identifier for a user account

    .. py:type:: ConnectionPool
        :canonical: list[ object ]

        Pool of database connections

    .. py:type:: ConfigDict
        :canonical: dict[ str, str | int | bool ]

        Configuration dictionary mapping strings to values


Scanning Unannotated Attributes
===============================================================================

Like classes, modules can contain attributes without type annotations. You can
enable scanning of these attributes to include them in documentation:

.. code-block:: python

    # settings.py
    ''' Application settings and configuration values. '''

    import dynadoc
    from typing import Annotated

    # Annotated configuration
    API_VERSION: Annotated[ str, dynadoc.Doc( "Current API version" ) ] = "v2"
    DEBUG: Annotated[ bool, dynadoc.Doc( "Debug mode flag" ) ] = False

    # Legacy constants without annotations
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    ALLOWED_HOSTS = [ "localhost", "127.0.0.1" ]
    _INTERNAL_SECRET = "hidden"  # Private, won't be documented

    # Configure module introspection to scan unannotated attributes
    module_introspection = dynadoc.IntrospectionControl(
        module_control = dynadoc.ModuleIntrospectionControl(
            scan_attributes = True
        )
    )

    dynadoc.assign_module_docstring(
        __name__,
        introspection = module_introspection
    )

This would generate documentation for both annotated and unannotated module
attributes:

.. code-block:: text

    Application settings and configuration values.

    .. py:data:: API_VERSION
        :type: str
        :value: 'v2'

    .. py:data:: DEBUG
        :type: bool
        :value: False

    .. py:data:: DEFAULT_TIMEOUT
        :value: 30

    .. py:data:: MAX_RETRIES
        :value: 3

    .. py:data:: ALLOWED_HOSTS
        :value: ['localhost', '127.0.0.1']

The ``scan_attributes`` feature helps document legacy modules that mix
annotated and unannotated attributes, ensuring comprehensive documentation
coverage without requiring extensive refactoring.


Package Initialization with Recursive Documentation
===============================================================================

Package ``__init__.py`` files often benefit from recursive documentation to
automatically document all exported classes and functions:

.. code-block:: python

    # mypackage/__init__.py
    ''' A comprehensive data processing package. '''

    import dynadoc
    from typing import Annotated

    from .core import DataProcessor, ValidationError
    from .utils import format_output, parse_input

    # Package-level constants
    DEFAULT_TIMEOUT: Annotated[ int, dynadoc.Doc( "Default timeout in seconds" ) ] = 30
    MAX_RETRIES: Annotated[ int, dynadoc.Doc( "Maximum retry attempts" ) ] = 3

    # Configure recursive documentation for functions and classes
    introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function | dynadoc.IntrospectionTargets.Class
    )

    dynadoc.assign_module_docstring(
        __name__,
        introspection = introspection
    )

This would automatically generate documentation for the package constants and
recursively document all imported classes and functions that have rich
annotations.


Real-World Example: dynadoc Self-Documentation
===============================================================================

The ``dynadoc`` package demonstrates this pattern by documenting itself. In its
``__init__.py`` file, you can see:

.. code-block:: python

    # From dynadoc/__init__.py
    _context = produce_context( notifier = _notify )
    _introspection_cc = ClassIntrospectionControl(
        inheritance = True,
        introspectors = ( introspection.introspect_special_classes, ) )
    _introspection = IntrospectionControl(
        class_control = _introspection_cc,
        targets = IntrospectionTargetsOmni )
    assign_module_docstring(
        __.package_name,
        context = _context,
        introspection = _introspection,
        table = __.fragments )

This creates comprehensive documentation for the entire ``dynadoc`` package,
including all classes, functions, and module attributes. The ``fragments``
table provides reusable documentation snippets, and the omnidirectional
introspection targets ensure complete coverage.


Automatic __all__ Support
===============================================================================

The ``dynadoc`` library automatically respects ``__all__`` declarations in
modules, providing intuitive control over which attributes are documented:

.. code-block:: python

    # api.py
    ''' Public API module with controlled exports. '''

    import dynadoc
    from typing import Annotated

    __all__ = [ 'PUBLIC_CONSTANT', 'main_function' ]

    # This will be documented (in __all__)
    PUBLIC_CONSTANT: Annotated[ int, dynadoc.Doc( "Public configuration value" ) ] = 42

    # This will not be documented (not in __all__)
    _private_setting: Annotated[ str, dynadoc.Doc( "Internal setting" ) ] = "internal"

    def main_function(
        value: Annotated[ int, dynadoc.Doc( "Input value" ) ]
    ) -> Annotated[ int, dynadoc.Doc( "Processed result" ) ]:
        ''' Main processing function. '''
        return value * 2

    # This will not be documented (not in __all__)
    def _internal_helper( value: int ) -> int:
        ''' Internal helper function. '''
        return value + 1

    dynadoc.assign_module_docstring( __name__ )

When ``__all__`` is present, only attributes listed in it will be documented,
regardless of their naming or annotation status. When ``__all__`` is absent,
the library falls back to standard visibility rules (non-underscore prefixed
names and annotated attributes).


Module Documentation Best Practices
===============================================================================

When documenting modules with ``dynadoc``:

**Use clear module docstrings** that describe the module's purpose::

    ''' High-level module for data validation and transformation.

        This module provides the primary interface for validating
        incoming data and transforming it for downstream processing.
    '''

**Document module-level constants** with meaningful descriptions::

    MAX_FILE_SIZE: Annotated[ int, dynadoc.Doc(
        "Maximum file size in bytes for upload processing"
    ) ] = 10 * 1024 * 1024

**Use TypeAlias for complex types** to improve code readability::

    ValidationResult: Annotated[ TypeAlias, dynadoc.Doc(
        "Result of data validation containing status and error details"
    ) ] = tuple[ bool, list[ str ] ]

**Enable recursive introspection** for packages to automatically document
exported functionality::

    introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function | dynadoc.IntrospectionTargets.Class
    )
    dynadoc.assign_module_docstring( __name__, introspection = introspection )
