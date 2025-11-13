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
Filesystem Organization
*******************************************************************************

This document describes the specific filesystem organization for the project,
showing how the standard organizational patterns are implemented for this
project's configuration. For the underlying principles and rationale behind
these patterns, see the `common architecture documentation
<https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_.

Project Structure
===============================================================================

Root Directory Organization
-------------------------------------------------------------------------------

The project implements the standard filesystem organization:

.. code-block::

    python-dynadoc/
    ├── LICENSE.txt              # Project license
    ├── README.rst               # Project overview and quick start
    ├── pyproject.toml           # Python packaging and tool configuration
    ├── documentation/           # Sphinx documentation source
    ├── sources/                 # All source code
    ├── tests/                   # Test suites
    └── .auxiliary/              # Development workspace

Source Code Organization
===============================================================================

Package Structure
-------------------------------------------------------------------------------

The main Python package follows the standard ``sources/`` directory pattern:

.. code-block::

    sources/
    └── dynadoc/                     # Main Python package
        ├── __/                      # Centralized import hub
        │   ├── __init__.py          # Re-exports core utilities
        │   ├── doctab.py            # Documentation fragment tables
        │   ├── imports.py           # External library imports
        │   └── nomina.py            # Project-specific naming constants
        ├── renderers/               # Rendering subsystem
        │   ├── __init__.py          # Renderer exports
        │   ├── __.py                # Renderer-specific imports
        │   └── sphinxad.py          # Sphinx Autodoc reStructuredText renderer
        ├── __init__.py              # Package entry point
        ├── assembly.py              # Docstring assembly and decoration
        ├── context.py               # Context and control data structures
        ├── factories.py             # Factory functions for contexts
        ├── interfaces.py            # Protocols and data classes
        ├── introspection.py         # Object introspection and annotation processing
        ├── nomina.py                # Top-level type aliases and constants
        ├── py.typed                 # Type checking marker
        ├── userapi.py               # Public API exports
        └── xtnsapi.py               # Extension API exports

All package modules use the standard ``__`` import pattern as documented
in the common architecture guide.

Module Responsibilities
-------------------------------------------------------------------------------

**Core User Interface**

* ``__init__.py``: Package entry point, self-documents via introspection
* ``userapi.py``: Exports user-facing API elements for import
* ``assembly.py``: Provides ``with_docstring`` decorator and
  ``assign_module_docstring`` function

**Processing Pipeline**

* ``introspection.py``: Introspects objects, reduces annotations, extracts
  documentation metadata
* ``assembly.py``: Orchestrates decoration, fragment collection, and recursive
  processing
* ``renderers/sphinxad.py``: Renders information objects as reStructuredText

**Configuration and Extension**

* ``context.py``: Defines ``Context`` and ``IntrospectionControl`` data
  structures with immutable configuration
* ``factories.py``: Provides ``produce_context`` factory with sensible defaults
* ``interfaces.py``: Defines protocols (``Notifier``, ``Renderer``,
  ``VisibilityDecider``, ``FragmentRectifier``) and data classes
  (``Doc``, ``Raises``, ``Default``, information classes)
* ``xtnsapi.py``: Re-exports extension API for custom renderers and
  introspectors

**Supporting Infrastructure**

* ``nomina.py``: Type aliases and constants used throughout package
* ``__/imports.py``: Centralized external imports (dataclasses, enum, inspect,
  re, types, typing, warnings, etc.)
* ``__/nomina.py``: Internal naming conventions and type definitions
* ``__/doctab.py``: Fragment table for package self-documentation

Subpackage: Renderers
-------------------------------------------------------------------------------

The ``renderers`` subpackage provides output format implementations:

* ``sphinxad.py``: Default renderer producing Sphinx Autodoc-compatible
  reStructuredText with field lists (``:argument:``, ``:type:``, ``:returns:``,
  ``:rtype:``, ``:raises:``)
* Future renderers could support Markdown, NumPy/Google docstring styles, etc.

Each renderer follows the ``Renderer`` protocol from ``interfaces.py``,
accepting a possessor object, information sequence, and context, returning a
formatted string.

Component Integration
===============================================================================

Module Dependencies
-------------------------------------------------------------------------------

The package follows a layered dependency structure:

* **Layer 0**: ``__/imports.py`` (external dependencies only)
* **Layer 1**: ``nomina.py``, ``__/nomina.py`` (type definitions)
* **Layer 2**: ``interfaces.py`` (protocols and data structures)
* **Layer 3**: ``context.py``, ``factories.py`` (configuration)
* **Layer 4**: ``introspection.py``, ``renderers/sphinxad.py`` (processing)
* **Layer 5**: ``assembly.py`` (orchestration)
* **Layer 6**: ``userapi.py``, ``xtnsapi.py``, ``__init__.py`` (public APIs)

This layering ensures that configuration is independent of processing logic,
and protocols are defined before implementations.

Public API Surface
-------------------------------------------------------------------------------

**User API** (``dynadoc.*``):

* Decorators: ``with_docstring``, ``exclude``
* Functions: ``assign_module_docstring``, ``produce_context``
* Annotation classes: ``Doc``, ``Fname``, ``Raises``, ``Default``
* Enums: ``Visibilities``, ``ValuationModes``, ``NotificationLevels``
* Protocols: ``Notifier``, ``Renderer``, ``VisibilityDecider``,
  ``FragmentRectifier``
* Configuration: ``Context``, ``IntrospectionControl``,
  ``ClassIntrospectionControl``, ``ModuleIntrospectionControl``

**Extension API** (``dynadoc.xtnsapi.*``):

Includes all user API plus internal utilities for renderer and introspector
implementations:

* ``introspect``: Main introspection entry point
* ``reduce_annotation``: Annotation reduction with cache
* Information classes: ``ArgumentInformation``, ``AttributeInformation``,
  ``ReturnInformation``, ``ExceptionInformation``
* Additional support types: ``AnnotationsCache``, ``AdjunctsData``

Testing Organization
-------------------------------------------------------------------------------

Tests mirror the source structure under ``tests/dynadoc/``:

* Unit tests for each module (``test_introspection.py``,
  ``test_assembly.py``, ``test_renderers_sphinxad.py``)
* Integration tests exercising full decoration pipeline
* Doctest examples in ``documentation/examples/``

Documentation Organization
-------------------------------------------------------------------------------

Documentation follows standard structure:

* ``documentation/examples/``: User-focused examples with executable doctests
* ``documentation/architecture/``: System design and architectural decisions
* Sphinx autodoc processes the package itself, dogfooding dynadoc's
  capabilities

Architecture Evolution
===============================================================================

This filesystem organization provides a foundation for future growth:

**Potential Extensions**

* Additional renderers in ``renderers/`` for other documentation formats
* Introspector registry in ``introspection.py`` for pluggable class handlers
* Type annotation filters in ``context.py`` for custom type transformations
* Resolver subsystem for handling forward references and stringified
  annotations

For questions about organizational principles, subpackage patterns, or testing
strategies, refer to the comprehensive common documentation:

* `Architecture Patterns <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/architecture.rst>`_
* `Development Practices <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/practices.rst>`_
* `Test Development Guidelines <https://raw.githubusercontent.com/emcd/python-project-common/refs/tags/docs-1/documentation/common/tests.rst>`_
