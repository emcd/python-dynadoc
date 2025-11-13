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
Product Requirements Document
*******************************************************************************

Executive Summary
===============================================================================

Dynadoc is a Python library that bridges the gap between modern rich type
annotations (PEP 727 ``Doc`` objects, ``Raises`` specifications, and other
annotation metadata) and automatic documentation generation tools like Sphinx
Autodoc. By introspecting annotated Python objects and extracting embedded
documentation metadata, Dynadoc generates comprehensive, formatted docstrings
that integrate seamlessly with existing documentation workflows.

The library enables Python developers to write documentation once—as
annotation metadata—and automatically generate polished docstrings without
manual duplication or maintenance overhead.

Problem Statement
===============================================================================

Modern Python encourages rich type annotations through ``Annotated`` types and
metadata objects like ``Doc`` from PEP 727. However, documentation tools like
Sphinx Autodoc cannot directly process this embedded metadata, forcing
developers to choose between:

1. **Manual duplication**: Writing the same information twice—once in
   annotations and again in docstrings—leading to maintenance burden and
   documentation drift
2. **Incomplete documentation**: Relying solely on type hints without
   descriptive documentation, resulting in poor developer experience
3. **Custom tooling**: Building project-specific solutions that don't
   generalize or integrate with standard documentation pipelines

This problem affects Python library maintainers, API developers, and teams
adopting modern typing practices. The consequences include:

* Increased maintenance cost from keeping annotations and docstrings
  synchronized
* Documentation quality degradation as projects evolve
* Inconsistent documentation styles across codebases
* Reduced adoption of rich annotation metadata due to lack of tooling support

Current workarounds involve writing custom Sphinx extensions or manually
copying annotation metadata into docstrings, neither of which provides a
reusable, standardized solution.

Goals and Objectives
===============================================================================

Primary Objectives
-------------------------------------------------------------------------------

* **REQ-GOAL-001** [Critical]: Extract documentation from PEP 727 ``Doc``
  objects and render as Sphinx-compatible docstrings

  *Success metric*: 100% of ``Doc`` annotations successfully extracted and
  formatted

* **REQ-GOAL-002** [Critical]: Support exception documentation via ``Raises``
  annotations in return types

  *Success metric*: All ``Raises`` specifications correctly rendered as
  ``:raises:`` directives

* **REQ-GOAL-003** [Critical]: Preserve existing docstring content while
  augmenting with generated documentation

  *Success metric*: Original docstrings retained when ``preserve=True``

* **REQ-GOAL-004** [High]: Enable recursive documentation of modules, classes,
  and functions

  *Success metric*: Configurable introspection targets process entire package
  hierarchies

Secondary Objectives
-------------------------------------------------------------------------------

* **REQ-GOAL-005** [Medium]: Support custom renderers for alternative output
  formats beyond Sphinx

  *Success metric*: Protocol-based extension points allow third-party renderers

* **REQ-GOAL-006** [Medium]: Provide visibility controls for attribute
  documentation

  *Success metric*: Custom visibility deciders filter attributes based on
  project-specific rules

* **REQ-GOAL-007** [Low]: Support fragment tables for reusable documentation
  snippets

  *Success metric*: Named fragments referenced from multiple locations

Target Users
===============================================================================

Primary User Personas
-------------------------------------------------------------------------------

**Library Maintainers**

* Build and maintain public Python libraries
* Need comprehensive API documentation for users
* Value consistency and maintainability
* Technical proficiency: Advanced Python developers
* Usage context: Documentation generation during package builds

**API Developers**

* Design and document internal and external APIs
* Require detailed parameter and return value documentation
* Work in teams with documentation standards
* Technical proficiency: Intermediate to advanced Python developers
* Usage context: Development and CI/CD pipelines

**Type Annotation Adopters**

* Migrating codebases to use modern Python typing features
* Want to leverage existing type annotations for documentation
* Seek to reduce duplication between types and docstrings
* Technical proficiency: Intermediate Python developers familiar with typing
* Usage context: Brownfield projects adding documentation

User Needs and Motivations
-------------------------------------------------------------------------------

* **Reduce maintenance burden**: Write documentation once, generate
  comprehensive docstrings automatically
* **Ensure consistency**: Synchronize type information and documentation
  without manual effort
* **Integrate with existing tools**: Work with Sphinx, mypy, and other
  standard Python tooling
* **Customize output**: Control what gets documented and how it appears
* **Adopt incrementally**: Add to existing projects without major refactoring

Functional Requirements
===============================================================================

Core Decoration
-------------------------------------------------------------------------------

**REQ-FUNC-001** [Critical]: Function Decoration

  As a library developer, I want to decorate functions with ``@with_docstring()``
  so that parameter and return documentation is automatically generated from
  annotations.

  Acceptance Criteria:
  - Decorator accepts functions with annotated parameters
  - ``Doc`` metadata extracted from ``Annotated`` types
  - Generated docstring includes ``:argument:``, ``:type:``, ``:returns:``,
    and ``:rtype:`` fields
  - Existing docstring content preserved when ``preserve=True``
  - Works with positional, keyword-only, and variadic parameters

**REQ-FUNC-002** [Critical]: Class Decoration

  As a library developer, I want to decorate classes with ``@with_docstring()``
  so that class and instance attributes are documented from annotations.

  Acceptance Criteria:
  - Decorator processes class-level annotations
  - Distinguishes between class variables (``ClassVar``) and instance
    variables
  - Generated docstring includes ``:cvar:`` and ``:ivar:`` fields
  - Supports inheritance of annotations when configured
  - Handles properties and descriptors appropriately

**REQ-FUNC-003** [Critical]: Module Documentation

  As a library developer, I want to call ``assign_module_docstring()`` so that
  module-level attributes are documented from annotations.

  Acceptance Criteria:
  - Accepts module object or string module name
  - Processes module-level annotated variables
  - Respects ``__all__`` for visibility when present
  - Handles ``TypeAlias`` annotations specially
  - Generates ``:py:data::`` and ``:py:type::`` directives

Annotation Processing
-------------------------------------------------------------------------------

**REQ-FUNC-004** [Critical]: Doc Extraction

  As a library developer, I want ``Doc`` objects in annotations to be
  extracted and used as documentation text so that I can write descriptions
  alongside type information.

  Acceptance Criteria:
  - ``Annotated[type, Doc("description")]`` extracts "description"
  - Multiple ``Doc`` objects concatenated with proper spacing
  - Multiline descriptions formatted correctly with indentation
  - Works for parameters, returns, and attributes

**REQ-FUNC-005** [Critical]: Raises Documentation

  As a library developer, I want ``Raises`` annotations in return types to
  document exceptions so that users know what errors to expect.

  Acceptance Criteria:
  - ``Raises(ExceptionClass, "description")`` generates ``:raises:`` field
  - Supports single exception class or sequence of classes
  - Multiple ``Raises`` annotations processed independently
  - Description optional (produces field without description text)

**REQ-FUNC-006** [High]: Complex Type Reduction

  As a library developer, I want complex generic types to be formatted
  readably so that documentation is understandable.

  Acceptance Criteria:
  - Union types rendered as ``type1 | type2``
  - Generic types rendered as ``Container[ElementType]``
  - Nested generics handled recursively
  - Forward references and string annotations handled gracefully
  - Cycle detection prevents infinite recursion

Customization
-------------------------------------------------------------------------------

**REQ-FUNC-007** [High]: Custom Renderers

  As an advanced user, I want to provide a custom renderer so that I can
  generate documentation in formats other than Sphinx reStructuredText.

  Acceptance Criteria:
  - ``Renderer`` protocol defines extension interface
  - Custom renderer receives possessor, informations, and context
  - Renderer can access annotation details and descriptions
  - Multiple output styles supported (e.g., Markdown, Google-style docstrings)

**REQ-FUNC-008** [High]: Visibility Control

  As a library maintainer, I want to control which attributes are documented
  so that I can hide internal implementation details.

  Acceptance Criteria:
  - ``Visibilities.Conceal`` annotation forces attribute hiding
  - ``Visibilities.Reveal`` annotation forces attribute documentation
  - Custom ``VisibilityDecider`` callback for complex rules
  - Default visibility based on naming conventions (``_private`` hidden)
  - Respects ``__all__`` in modules

**REQ-FUNC-009** [Medium]: Introspection Control

  As a library developer, I want to configure which object types are
  recursively documented so that I can control documentation scope.

  Acceptance Criteria:
  - ``IntrospectionControl.targets`` specifies classes, functions, modules,
    descriptors
  - Per-object ``_dynadoc_introspection_limit_`` attribute overrides global
    settings
  - Inheritance handling configurable per class
  - Attribute scanning can be enabled or disabled
  - Maximum recursion depth implicitly controlled by targets

**REQ-FUNC-010** [Medium]: Fragment Tables

  As a documentation author, I want to define reusable documentation fragments
  so that common descriptions can be referenced multiple places.

  Acceptance Criteria:
  - Fragment table passed as ``table`` parameter
  - ``Fname("fragment_name")`` annotation references table entries
  - String fragments in decorator arguments look up table values
  - Missing fragment names generate errors via notifier
  - Fragments can come from module attributes (``_dynadoc_fragments_``)

Configuration
-------------------------------------------------------------------------------

**REQ-FUNC-011** [High]: Context Configuration

  As a library developer, I want to configure behavior via ``Context`` objects
  so that I can customize the documentation generation process.

  Acceptance Criteria:
  - ``produce_context()`` factory creates context with defaults
  - Customizable notifier for warnings and errors
  - Customizable fragment rectifier for text normalization
  - Customizable visibility decider for attribute filtering
  - Immutable context objects prevent accidental modification

**REQ-FUNC-012** [Medium]: Default Value Handling

  As a library developer, I want to control how default values are documented
  so that I can suppress or replace them as needed.

  Acceptance Criteria:
  - ``Default(mode=ValuationModes.Accept)`` uses actual default value
  - ``Default(mode=ValuationModes.Suppress)`` omits default from documentation
  - ``Default(mode=ValuationModes.Surrogate, surrogate="value")`` shows
    alternative
  - Applied via annotation metadata
  - Works for function parameters and class/module attributes

Non-Functional Requirements
===============================================================================

Performance
-------------------------------------------------------------------------------

**REQ-PERF-001** [High]: Annotation caching prevents redundant type processing

  *Metric*: Each unique annotation processed at most once per decoration

**REQ-PERF-002** [Medium]: Decoration overhead acceptable for import-time
execution

  *Metric*: Package with 100 decorated functions imports in under 1 second on
  modern hardware

Correctness
-------------------------------------------------------------------------------

**REQ-CORR-001** [Critical]: Cycle detection prevents infinite recursion

  *Metric*: Self-referential types (e.g., ``Tree[Tree[T]]``) handled without
  stack overflow

**REQ-CORR-002** [Critical]: Multiple decoration of same object prevented

  *Metric*: Weak reference tracking ensures each object decorated exactly once

**REQ-CORR-003** [High]: Malformed annotations handled gracefully

  *Metric*: Invalid annotation metadata generates warnings, not exceptions

Compatibility
-------------------------------------------------------------------------------

**REQ-COMPAT-001** [Critical]: Python 3.11+ support

  *Metric*: All features work on Python 3.11, 3.12, 3.13

**REQ-COMPAT-002** [Critical]: Sphinx Autodoc compatibility

  *Metric*: Generated docstrings parse correctly with sphinx.ext.autodoc

**REQ-COMPAT-003** [High]: Type checker compatibility

  *Metric*: No false positives from mypy or pyright when using dynadoc

**REQ-COMPAT-004** [Medium]: No runtime dependency on typing_extensions after
Python 3.13

  *Metric*: Uses stdlib ``Doc`` when available, fallback for earlier versions

Usability
-------------------------------------------------------------------------------

**REQ-USE-001** [High]: Clear error messages for common mistakes

  *Metric*: Fragment not found, invalid annotation, and other errors provide
  actionable guidance

**REQ-USE-002** [Medium]: Sensible defaults require minimal configuration

  *Metric*: ``@with_docstring()`` works without parameters for typical use
  cases

**REQ-USE-003** [Medium]: API follows Python conventions

  *Metric*: Decorator and function names follow PEP 8, parameter names are
  descriptive

Extensibility
-------------------------------------------------------------------------------

**REQ-EXT-001** [High]: Protocol-based extension points

  *Metric*: Custom renderers, notifiers, visibility deciders, fragment
  rectifiers implementable without subclassing

**REQ-EXT-002** [Medium]: Custom class introspectors

  *Metric*: Special class types (Enum, dataclass, etc.) can have specialized
  introspection logic

Constraints and Assumptions
===============================================================================

Technical Constraints
-------------------------------------------------------------------------------

* Python 3.11+ required for modern ``typing`` features and ``inspect`` APIs
* Depends on Python stdlib modules: ``dataclasses``, ``enum``, ``inspect``,
  ``re``, ``types``, ``typing``, ``warnings``
* Optional dependency on ``typing_extensions`` for ``Doc`` fallback on Python
  < 3.13
* Docstring generation happens at decoration time (import time or explicit
  call), not lazily

Design Assumptions
-------------------------------------------------------------------------------

* Users follow PEP 727 ``Doc`` object conventions for annotation metadata
* Annotated types use ``Annotated[type, metadata]`` syntax from PEP 593
* Target documentation system supports Sphinx-style field lists (or custom
  renderer provided)
* Module, class, and function docstrings are mutable (``__doc__`` writable)
* Weak references to decorated objects are viable for visit tracking

Behavioral Assumptions
-------------------------------------------------------------------------------

* Users want to preserve existing docstrings by default
* Public attributes (no leading underscore) should be documented by default
* Module ``__all__`` indicates exhaustive list of public API when present
* Introspection should be conservative by default (no recursive targets)

Out of Scope
===============================================================================

The following features are explicitly excluded from the current product scope:

**Alternative Documentation Standards**

* Direct support for NumPy docstring format (can be added via custom renderer)
* Direct support for Google docstring format (can be added via custom renderer)
* Direct support for Markdown output (can be added via custom renderer)

**Advanced Type Resolution**

* Automatic resolution of all stringified annotations (forward references
  handled on best-effort basis)
* Integration with type checkers for type inference
* Runtime type validation or checking

**Documentation Generation**

* Building Sphinx documentation (Dynadoc generates docstrings; Sphinx builds
  docs)
* Generating standalone API documentation files
* Creating tutorials or user guides from code

**IDE and Tooling Integration**

* IDE plugins or language server extensions
* Direct integration with documentation hosting platforms
* Version control integration for tracking documentation changes

**Behavioral Modifications**

* Modifying Python's annotation semantics or evaluation
* Monkey-patching core typing or inspect modules
* Runtime performance optimization beyond caching

**Project Management**

* Sprint planning or development timelines are not included in this PRD
* Resource allocation and team assignments are determined separately