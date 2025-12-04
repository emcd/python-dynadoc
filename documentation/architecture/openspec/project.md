# Project Context

## Purpose

Dynadoc bridges rich Python type annotations and automatic documentation generation. It extracts metadata from `Annotated` types (particularly PEP 727 `Doc` objects) and produces formatted docstrings compatible with Sphinx Autodoc.

**Core Problem**: Documentation tools like Sphinx Autodoc cannot directly process embedded annotation metadata. Dynadoc solves this by introspecting annotated Python objects, extracting documentation from `Doc` objects and `Raises` specifications, and generating comprehensive reStructuredText docstrings.

**Key Capabilities**:
- Docstring generation for modules, classes, functions, and methods via introspection
- Reusable documentation fragments for consistent terminology
- Protocol-based extensibility for custom renderers and visibility rules
- Sphinx-compatible output by default

## Tech Stack

- Python 3.10+ (supports 3.10, 3.11, 3.12, 3.13, 3.14, PyPy 3.10, PyPy 3.11)
- typing-extensions (for PEP 727 `Doc` support)
- Hatch (build system and environment management)
- Sphinx (documentation generation)
- Pytest with Coverage (testing)
- Ruff, Pyright, isort (linting and type checking)

## Project Conventions

### Filesystem Organization

See [documentation/architecture/filesystem.rst](../filesystem.rst) for comprehensive details.

**Root Structure**:
```
python-dynadoc/
├── sources/dynadoc/     # Main Python package
├── tests/               # Test suites mirroring source structure
├── documentation/       # Sphinx documentation source
└── .auxiliary/          # Development workspace (caches, artifacts, configuration)
```

**Import Hub Pattern**: All modules use the `__` import hub pattern. External imports are centralized in `__/imports.py`, and modules import via `from . import __`.

**API Modules**: `userapi.py` and `xtnsapi.py` are designated import hubs that re-export public and extension APIs respectively.

### Architecture Patterns

See [documentation/architecture/summary.rst](../summary.rst) for the system overview.

**Pipeline Architecture**: Four primary layers - Introspection, Assembly, Rendering, Context/Configuration.

**Protocol-Based Extensibility**: Key extension points (`Notifier`, `Renderer`, `VisibilityDecider`, `FragmentRectifier`, `ClassIntrospector`) use protocols rather than inheritance.

**Immutable Configuration**: All configuration objects (`Context`, `IntrospectionControl`) are frozen dataclasses. Changes create new instances via methods like `with_limit()`.

**Layered Dependencies**: Modules follow a strict dependency hierarchy from Layer 0 (external imports) through Layer 6 (public APIs).

### Code Style

Follow the [common code style guide](https://emcd.github.io/python-project-common/stable/sphinx-html/common/style.html):
- Spaces around brackets for readability: `function( arg1, arg2 )`
- Narrow `try` blocks wrapping only the statement that may raise
- Type annotations on all public APIs
- Frozen dataclasses for configuration objects

### Testing Strategy

- Unit tests mirror source structure under `tests/dynadoc/`
- Doctest examples in `documentation/examples/` executed via Sphinx
- 100% code coverage target
- Run with: `hatch --env develop run testers`

### Git Workflow

- Signed commits required
- Present tense, imperative mood commit messages (e.g., "Fix" not "Fixed")
- Towncrier changelog fragments in `.auxiliary/data/towncrier/`
- Pre-commit hooks run validation automatically

## Domain Context

**PEP 727**: The withdrawn PEP proposed `Doc` objects for embedding documentation in type annotations. While not adopted into Python, `typing_extensions` maintains `Doc` indefinitely. Dynadoc provides a fallback implementation if needed.

**Annotation Reduction**: Complex type annotations like `Annotated[str, Doc("description")]` are "reduced" to extract base types and metadata separately.

**Fragment Tables**: Reusable documentation snippets stored in mappings, referenced by name via `Fname` annotations.

## Important Constraints

- Must maintain backward compatibility with existing `@with_docstring` decorator usage
- Sphinx Autodoc compatibility is the primary output target
- No modification of Python's annotation semantics
- Thread-safe through immutable configuration objects

## External Dependencies

- **typing_extensions**: Provides `Doc` class (PEP 727 implementation)
- **Sphinx Autodoc**: Primary documentation consumer
- **python-project-common**: Shared development practices and Copier templates
- **agents-common**: AI assistant configuration templates
