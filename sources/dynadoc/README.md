# Dynadoc Architecture

Dynadoc is a Python library that bridges rich type annotations and automatic
documentation generation by extracting metadata from annotations and producing
formatted docstrings compatible with Sphinx Autodoc.

## Core Purpose

Modern Python supports rich type annotations through `Annotated` types and
metadata objects like `Doc` from [PEP 727](https://peps.python.org/pep-0727/).
However, documentation tools like Sphinx Autodoc cannot directly process this
embedded metadata. Dynadoc solves this problem by:

* Introspecting annotated Python objects (modules, classes, functions)
* Extracting documentation from `Doc` objects, `Raises` specifications,
  and other annotation metadata
* Generating comprehensive, formatted docstrings from this metadata
* Supporting customizable rendering for different documentation formats

## Major Components

The system architecture follows a pipeline pattern with four primary layers:

### Introspection Layer

**Location**: `introspection.py`

Examines Python objects to extract documentable information:

* **Annotation Access**: Retrieves annotations from modules, classes, and
  functions using `inspect.get_annotations`
* **Annotation Reduction**: Processes complex generic types (`List[T]`,
  `Dict[K,V]`, `Annotated[T, ...]`) to extract base types and metadata
* **Information Extraction**: Creates structured information objects
  (`ArgumentInformation`, `AttributeInformation`, `ReturnInformation`,
  `ExceptionInformation`) from annotations
* **Cycle Detection**: Uses annotation cache to prevent infinite recursion
  when processing self-referential types
* **Special Class Handling**: Supports custom introspectors for special types
  (e.g., `Enum` members as class variables)

The introspection system distinguishes between class attributes, instance
attributes, and module attributes based on annotation metadata (`ClassVar`)
and introspection control settings.

### Assembly Layer

**Location**: `assembly.py`

Orchestrates docstring generation and object decoration:

* **Entry Points**: Provides `with_docstring` decorator for functions/classes,
  `assign_module_docstring` for modules, and `exclude` decorator to prevent
  objects from being processed during recursive decoration
* **Fragment Collection**: Gathers docstring fragments from multiple sources:
  existing docstrings, explicit fragment arguments, fragment tables, and
  introspection results
* **Recursive Decoration**: Processes module and class attributes based on
  introspection targets (functions, classes, descriptors, nested modules)
* **Visit Tracking**: Uses weak references to prevent duplicate decoration of
  the same object
* **Introspection Limiting**: Applies per-object limits through special
  attributes (`_dynadoc_introspection_limit_`)

The assembly layer coordinates between introspection and rendering, combining
all fragments into a final docstring.

### Rendering Layer

**Location**: `renderers/`

Converts structured information into formatted docstring text:

* **Sphinx Autodoc Renderer** (`sphinxad.py`): Default renderer producing
  reStructuredText compatible with Sphinx Autodoc
* **Annotation Formatting**: Converts type annotations to readable strings,
  handling unions, generics, literals, and forward references
* **Style Options**: Supports "Legible" (extra spacing) and "Pep8" (compact)
  formatting styles
* **Information Dispatch**: Routes different information types to specialized
  formatters for arguments, attributes, returns, and exceptions
* **Module Attribute Handling**: Special formatting for TypeAlias and data
  directives

The rendering system is protocol-based, allowing custom renderers to be
plugged in for different output formats.

### Context and Configuration

**Location**: `context.py`

Provides configuration and customization through immutable context objects:

* **Execution Context** (`Context`): Bundles customization points including
  notifier, fragment rectifier, visibility decider, and name resolution
  settings
* **Introspection Control** (`IntrospectionControl`): Configures introspection
  behavior including targets (which object types to process), inheritance
  handling, attribute scanning, and custom introspectors
* **Control Hierarchies**: Separate controls for class introspection
  (`ClassIntrospectionControl`) and module introspection
  (`ModuleIntrospectionControl`)
* **Limit Application**: Supports per-object introspection limits that
  override global settings

Context objects are immutable and frozen dataclasses, ensuring predictable
behavior throughout the processing pipeline.

## Data Flow

Docstring generation follows this sequence:

1. **Decoration Initiation**: User applies `@with_docstring()` decorator or
   calls `assign_module_docstring()`

2. **Fragment Collection**: Assembly layer gathers fragments from:

   * Existing docstring (if `preserve=True`)
   * Explicit fragments passed as arguments
   * Fragment table lookups
   * Object's `_dynadoc_fragments_` attribute

3. **Introspection** (if enabled):

   * Access annotations from object
   * Reduce complex annotations, extracting metadata
   * Create information objects for arguments, attributes, returns, exceptions
   * Apply visibility rules to filter attributes

4. **Rendering**: Convert information objects to formatted text using
   configured renderer

5. **Assembly**: Combine all fragments (existing docstring, explicit fragments,
   rendered introspection) with double newline separators

6. **Assignment**: Set `__doc__` attribute on target object

7. **Recursive Processing** (if targets configured): Repeat process for nested
   classes, functions, and modules

## Design Patterns

### Protocol-Based Extensibility

Key extension points use protocols rather than inheritance:

* `Notifier`: Custom warning and error handling
* `Renderer`: Alternative output formats beyond reStructuredText
* `VisibilityDecider`: Custom rules for attribute visibility
* `FragmentRectifier`: Custom fragment normalization
* `ClassIntrospector`: Special handling for non-standard class structures

This approach allows composition and runtime customization without subclassing.

### Annotation Reduction

Complex type annotations are "reduced" to simpler forms while extracting
metadata:

* `Annotated[str, Doc("name")]` → base type `str`, metadata `Doc("name")`
* `List[Dict[str, int]]` → recursively reduced with structure preserved
* Caching prevents redundant processing and detects reference cycles
* Forward references and string annotations handled gracefully

### Immutable Configuration

All configuration objects (`Context`, `IntrospectionControl`, `Default`)
are frozen dataclasses. Changes create new instances through methods like
`with_limit()` and `with_invoker_globals()`, ensuring thread-safety and
preventing accidental mutation.

### Fragment Composition

Docstrings are built from composable fragments rather than monolithic
generation. Fragments can come from:

* Inline string literals
* `Doc` objects in annotations
* Named entries in fragment tables (reusable snippets)
* Existing docstrings on objects
* Rendered introspection results

This enables incremental documentation and reuse of common text across a
project.

## Module Responsibilities

### Core User Interface

* `__init__.py`: Package entry point, self-documents via introspection
* `userapi.py`: Exports user-facing API elements for import
* `assembly.py`: Provides `with_docstring` decorator and
  `assign_module_docstring` function

### Processing Pipeline

* `introspection.py`: Introspects objects, reduces annotations, extracts
  documentation metadata
* `assembly.py`: Orchestrates decoration, fragment collection, and recursive
  processing
* `renderers/sphinxad.py`: Renders information objects as reStructuredText

### Configuration and Extension

* `context.py`: Defines `Context` and `IntrospectionControl` data
  structures with immutable configuration
* `factories.py`: Provides `produce_context` factory with sensible defaults
* `interfaces.py`: Defines protocols (`Notifier`, `Renderer`,
  `VisibilityDecider`, `FragmentRectifier`) and data classes
  (`Doc`, `Raises`, `Default`, information classes)
* `xtnsapi.py`: Re-exports extension API for custom renderers and
  introspectors

### Supporting Infrastructure

* `nomina.py`: Type aliases and constants used throughout package
* `__/imports.py`: Centralized external imports (dataclasses, enum, inspect,
  re, types, typing, warnings, etc.)
* `__/nomina.py`: Internal naming conventions and type definitions
* `__/doctab.py`: Fragment table for package self-documentation

## Subpackage: Renderers

The `renderers` subpackage provides output format implementations:

* `sphinxad.py`: Default renderer producing Sphinx Autodoc-compatible
  reStructuredText with field lists (`:argument:`, `:type:`, `:returns:`,
  `:rtype:`, `:raises:`)
* Future renderers could support Markdown, NumPy/Google docstring styles, etc.

Each renderer follows the `Renderer` protocol from `interfaces.py`,
accepting a possessor object, information sequence, and context, returning a
formatted string.

## Module Dependencies

The package follows a layered dependency structure:

* **Layer 0**: `__/imports.py` (external dependencies only)
* **Layer 1**: `nomina.py`, `__/nomina.py` (type definitions)
* **Layer 2**: `interfaces.py` (protocols and data structures)
* **Layer 3**: `context.py`, `factories.py` (configuration)
* **Layer 4**: `introspection.py`, `renderers/sphinxad.py` (processing)
* **Layer 5**: `assembly.py` (orchestration)
* **Layer 6**: `userapi.py`, `xtnsapi.py`, `__init__.py` (public APIs)

This layering ensures that configuration is independent of processing logic,
and protocols are defined before implementations.

## Public API Surface

### User API (`dynadoc.*`)

* Decorators: `with_docstring`, `exclude`
* Functions: `assign_module_docstring`, `produce_context`
* Annotation classes: `Doc`, `Fname`, `Raises`, `Default`
* Enums: `Visibilities`, `ValuationModes`, `NotificationLevels`
* Protocols: `Notifier`, `Renderer`, `VisibilityDecider`,
  `FragmentRectifier`
* Configuration: `Context`, `IntrospectionControl`,
  `ClassIntrospectionControl`, `ModuleIntrospectionControl`

### Extension API (`dynadoc.xtnsapi.*`)

Includes all user API plus internal utilities for renderer and introspector
implementations:

* `introspect`: Main introspection entry point
* `reduce_annotation`: Annotation reduction with cache
* Information classes: `ArgumentInformation`, `AttributeInformation`,
  `ReturnInformation`, `ExceptionInformation`
* Additional support types: `AnnotationsCache`, `AdjunctsData`

## Quality Attributes

### Extensibility

* Protocol-based customization points for rendering and visibility
* Pluggable introspectors for special class types
* Configurable fragment rectification and error notification
* Support for custom annotation metadata beyond `Doc` and `Raises`

### Correctness

* Cycle detection prevents infinite recursion in self-referential types
* Visit tracking prevents duplicate decoration
* Immutable configuration prevents state corruption
* Graceful handling of annotation access failures and malformed metadata

### Performance

* Annotation cache reduces redundant type processing
* Weak reference tracking has minimal memory overhead
* Single-pass introspection and rendering
* Introspection can be selectively disabled or limited per object

### Integration

* Sphinx-compatible output by default
* Works with standard Python `inspect` and `typing` modules
* Preserves existing docstrings and tooling workflows
* No modification of Python's annotation semantics
