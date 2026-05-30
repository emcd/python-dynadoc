## ADDED Requirements

### Requirement: Python 3.14+ Annotation Access

The system SHALL support Python 3.14+ lazy annotation evaluation via
`__annotate__` descriptor and `annotationlib` module.

Priority: Critical

#### Scenario: Lazy Annotation Access
- **WHEN** running on Python 3.14+
- **AND** an object has `__annotate__` descriptor
- **THEN** the system uses `inspect.get_annotations` with appropriate format
- **AND** annotations are evaluated lazily on first access

#### Scenario: Forward Reference Format
- **WHEN** running on Python 3.14+
- **AND** FORWARDREF format is requested
- **THEN** the system returns annotations with ForwardRef proxy objects
- **AND** undefined names are represented as ForwardRef instances

#### Scenario: Source Format
- **WHEN** running on Python 3.14+
- **AND** SOURCE format is requested
- **THEN** the system returns annotations as source code strings
- **AND** documentation can use original source representation

### Requirement: Backward Compatibility via typing_extensions

The system SHALL use `typing_extensions` >= 4.13.0 to provide FORWARDREF
format support on Python 3.10-3.13.

Priority: Critical

#### Scenario: typing_extensions ForwardRef Support
- **WHEN** running on Python 3.10-3.13
- **AND** `typing_extensions` >= 4.13.0 is installed (required dependency)
- **THEN** the system uses `typing_extensions.get_annotations` with FORWARDREF format
- **AND** forward references are handled consistently across all Python versions

### Requirement: Forward Reference Resolution

The system SHALL handle forward references correctly in Python 3.14+
using FORWARDREF format when available.

Priority: High

#### Scenario: ForwardRef Proxy Handling
- **WHEN** an annotation contains ForwardRef proxy objects
- **THEN** the system processes them appropriately for documentation
- **AND** attempts to resolve them when possible

#### Scenario: Unresolvable Forward References
- **WHEN** a forward reference cannot be resolved
- **AND** FORWARDREF format is used
- **THEN** the system documents the reference using available information
- **AND** issues a warning via the notifier
