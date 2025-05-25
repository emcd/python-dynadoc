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

.. important::

   **Sphinx Documentation Limitation**

   Due to current limitations in Sphinx, the ``.. py:data::`` directive does
   not support injecting custom descriptions from annotations. While ``dynadoc``
   extracts and processes descriptions from ``Doc`` annotations on module
   attributes, these descriptions are preserved in the source code but do not
   appear in the rendered Sphinx output.

   This limitation does **not** affect type aliases, which use ``.. py:type::``
   and properly display descriptions, nor does it affect function and class
   documentation.

.. doctest:: Modules

    >>> import dynadoc
    >>> from typing import Annotated, TypeAlias


Basic Module Documentation
===============================================================================

Module-level annotations are documented by calling ``assign_module_docstring``
with the current module. You can pass either the module name as a string or
the actual module object:

.. code-block:: python

    # api_config.py
    ''' API configuration and connection settings. '''

    import dynadoc
    from typing import Annotated

    # Module-level configuration with documented annotations
    api_version: Annotated[ str, dynadoc.Doc( "Current API version identifier" ) ] = "v2.1"
    debug_enabled: Annotated[ bool, dynadoc.Doc( "Whether debug logging is active" ) ] = False
    max_connections: Annotated[ int, dynadoc.Doc( "Maximum concurrent API connections" ) ] = 100

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

    API configuration and connection settings.

    .. py:data:: api_version
        :type: str
        :value: 'v2.1'

    .. py:data:: debug_enabled
        :type: bool
        :value: False

    .. py:data:: max_connections
        :type: int
        :value: 100


TypeAlias Documentation
===============================================================================

Modules frequently define type aliases that benefit from rich documentation.
Unlike regular data attributes, type aliases properly display their descriptions:

.. code-block:: python

    # api_types.py
    ''' Type definitions for API client functionality. '''

    import dynadoc
    from typing import Annotated, TypeAlias

    # Type aliases with comprehensive documentation
    APIKey: Annotated[ TypeAlias, dynadoc.Doc( "Authentication key for API access" ) ] = str
    RequestHeaders: Annotated[ TypeAlias, dynadoc.Doc( "Dictionary of HTTP request headers" ) ] = dict[ str, str ]
    ResponseData: Annotated[ TypeAlias, dynadoc.Doc( "Parsed JSON response data from API endpoints" ) ] = dict[ str, str | int | bool ]

    dynadoc.assign_module_docstring( __name__ )

This generates clean documentation for the type aliases:

.. code-block:: text

    Type definitions for API client functionality.

    .. py:type:: APIKey
        :canonical: str

        Authentication key for API access

    .. py:type:: RequestHeaders
        :canonical: dict[ str, str ]

        Dictionary of HTTP request headers

    .. py:type:: ResponseData
        :canonical: dict[ str, str | int | bool ]

        Parsed JSON response data from API endpoints


Scanning Unannotated Attributes
===============================================================================

Like classes, modules can contain attributes without type annotations. You can
enable scanning of these attributes to include them in documentation:

.. code-block:: python

    # app_settings.py
    ''' Application settings and configuration values. '''

    import dynadoc
    from typing import Annotated

    # Annotated configuration
    API_VERSION: Annotated[ str, dynadoc.Doc( "Current API version" ) ] = "v2"
    DEBUG_MODE: Annotated[ bool, dynadoc.Doc( "Development debug flag" ) ] = False

    # Legacy constants without annotations
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    ALLOWED_FORMATS = [ "json", "xml", "yaml" ]
    _INTERNAL_TOKEN = "hidden"  # Private, won't be documented

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

    .. py:data:: DEBUG_MODE
        :type: bool
        :value: False

    .. py:data:: DEFAULT_TIMEOUT
        :value: 30

    .. py:data:: MAX_RETRIES
        :value: 3

    .. py:data:: ALLOWED_FORMATS
        :value: ['json', 'xml', 'yaml']

The ``scan_attributes`` feature helps document legacy modules that mix
annotated and unannotated attributes, ensuring comprehensive documentation
coverage without requiring extensive refactoring.


Package Initialization with Recursive Documentation
===============================================================================

Package ``__init__.py`` files often benefit from recursive documentation to
automatically document all exported classes and functions:

.. code-block:: python

    # data_processing/__init__.py
    ''' Comprehensive data processing and validation package. '''

    import dynadoc
    from typing import Annotated

    from .validators import DataValidator, ValidationError
    from .transformers import TextNormalizer, CSVParser

    # Package-level constants
    DEFAULT_ENCODING: Annotated[ str, dynadoc.Doc( "Default text encoding for file operations" ) ] = "utf-8"
    MAX_FILE_SIZE: Annotated[ int, dynadoc.Doc( "Maximum file size in bytes for processing" ) ] = 10 * 1024 * 1024

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

    # http_client.py
    ''' HTTP client module with controlled exports. '''

    import dynadoc
    from typing import Annotated

    __all__ = [ 'API_BASE_URL', 'create_client' ]

    # This will be documented (in __all__)
    API_BASE_URL: Annotated[ str, dynadoc.Doc( "Default base URL for API requests" ) ] = "https://api.example.com"

    # This will not be documented (not in __all__)
    _debug_token: Annotated[ str, dynadoc.Doc( "Internal debugging token" ) ] = "debug123"

    def create_client(
        api_key: Annotated[ str, dynadoc.Doc( "Authentication key" ) ]
    ) -> Annotated[ object, dynadoc.Doc( "Configured HTTP client instance" ) ]:
        ''' Create HTTP client with authentication. '''
        return object( )

    # This will not be documented (not in __all__)
    def _internal_helper( value: str ) -> str:
        ''' Internal helper function. '''
        return value.upper( )

    dynadoc.assign_module_docstring( __name__ )

When ``__all__`` is present, only attributes listed in it will be documented,
regardless of their naming or annotation status. When ``__all__`` is absent,
the library falls back to standard visibility rules (non-underscore prefixed
names and annotated attributes).


Configuration File Processing Example
===============================================================================

Here's a comprehensive example showing how module documentation works with
a configuration processing module:

.. code-block:: python

    # config_processor.py
    ''' Configuration file processing with multiple format support. '''

    import dynadoc
    from typing import Annotated, TypeAlias

    # Type aliases for configuration processing
    ConfigData: Annotated[ TypeAlias, dynadoc.Doc( "Dictionary containing parsed configuration data" ) ] = dict[ str, str | int | bool ]
    ConfigPath: Annotated[ TypeAlias, dynadoc.Doc( "File system path to configuration file" ) ] = str
    ValidationRules: Annotated[ TypeAlias, dynadoc.Doc( "Set of validation rules for configuration values" ) ] = dict[ str, callable ]

    # Module constants
    SUPPORTED_FORMATS: Annotated[ list[ str ], dynadoc.Doc( "List of supported configuration file formats" ) ] = [ "json", "yaml", "toml" ]
    DEFAULT_ENCODING: Annotated[ str, dynadoc.Doc( "Default text encoding for configuration files" ) ] = "utf-8"
    MAX_FILE_SIZE: Annotated[ int, dynadoc.Doc( "Maximum configuration file size in bytes" ) ] = 1024 * 1024

    def load_config(
        path: Annotated[ ConfigPath, dynadoc.Doc( "Path to configuration file to load" ) ],
        validate: Annotated[ bool, dynadoc.Doc( "Whether to validate configuration after loading" ) ] = True
    ) -> Annotated[ ConfigData, dynadoc.Doc( "Loaded and optionally validated configuration data" ) ]:
        ''' Load configuration from file with optional validation. '''
        return { }

    def validate_config(
        config: Annotated[ ConfigData, dynadoc.Doc( "Configuration data to validate" ) ],
        rules: Annotated[ ValidationRules, dynadoc.Doc( "Validation rules to apply" ) ]
    ) -> Annotated[ bool, dynadoc.Doc( "True if configuration passes all validation rules" ) ]:
        ''' Validate configuration data against specified rules. '''
        return True

    # Enable comprehensive documentation
    comprehensive_introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function,
        module_control = dynadoc.ModuleIntrospectionControl( scan_attributes = True )
    )

    dynadoc.assign_module_docstring( __name__, introspection = comprehensive_introspection )

This example demonstrates the full power of module documentation with type
aliases, annotated constants, function documentation, and comprehensive
introspection settings.


Module Documentation Best Practices
===============================================================================

When documenting modules with ``dynadoc``:

**Document module-level constants** with meaningful descriptions that explain
their purpose and usage::

    API_TIMEOUT: Annotated[ int, dynadoc.Doc(
        "Default timeout in seconds for API requests"
    ) ] = 30

**Use TypeAlias for complex types** to improve code readability and provide
comprehensive documentation that appears properly in Sphinx output::

    APIResponse: Annotated[ TypeAlias, dynadoc.Doc(
        "Standard API response format containing status and data"
    ) ] = dict[ str, str | int | list | dict ]

**Enable recursive introspection** for packages to automatically document
exported functionality without manual decoration::

    introspection = dynadoc.IntrospectionControl(
        targets = dynadoc.IntrospectionTargets.Function | dynadoc.IntrospectionTargets.Class
    )
    dynadoc.assign_module_docstring( __name__, introspection = introspection )

**Consider performance implications** when enabling comprehensive introspection
on large modules, and prefer targeted introspection when full coverage isn't
needed.

**Use fragment tables** to maintain consistent terminology across related
modules and reduce documentation maintenance overhead.
