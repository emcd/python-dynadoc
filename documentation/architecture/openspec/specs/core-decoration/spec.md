# Core Decoration

## Purpose
Enables automatic documentation generation for functions, classes, and modules by decorating them or explicitly assigning docstrings. It bridges the gap between Python's rich type annotations and documentation tools like Sphinx, ensuring that documentation lives alongside the code it describes.

## Requirements

### Requirement: Function Decoration
The `@with_docstring()` decorator SHALL generate parameter and return documentation from function annotations and assign it to the function's `__doc__` attribute.

Priority: Critical

#### Scenario: Basic Function Decoration
- **WHEN** a function is decorated with `@with_docstring()`
- **AND** the function has `Annotated` parameters with `Doc` metadata
- **THEN** the function's `__doc__` attribute contains Sphinx-formatted parameter documentation
- **AND** existing docstring content is preserved if `preserve=True`

#### Scenario: Keyword-only and Variadic Parameters
- **WHEN** a function has keyword-only or variadic parameters (`*args`, `**kwargs`)
- **THEN** they are correctly documented in the generated docstring

### Requirement: Class Decoration
The `@with_docstring()` decorator SHALL document class and instance attributes from class annotations when applied to a class.

Priority: Critical

#### Scenario: Class Attribute Documentation
- **WHEN** a class is decorated with `@with_docstring()`
- **AND** the class has `Annotated` attributes with `Doc` metadata
- **THEN** class variables are documented as `:cvar:`
- **AND** instance variables are documented as `:ivar:`

#### Scenario: Property Documentation
- **WHEN** a class has a property with a getter
- **THEN** the property is documented based on the getter's docstring and signature

### Requirement: Module Documentation
The `assign_module_docstring()` function SHALL document module-level attributes from module annotations.

Priority: Critical

#### Scenario: Module Attribute Documentation
- **WHEN** `assign_module_docstring(module)` is called
- **THEN** annotated module-level variables are documented
- **AND** `TypeAlias` annotations are documented as `:py:type:`
- **AND** other variables are documented as `:py:data:`

#### Scenario: Visibility Respect
- **WHEN** the module has `__all__` defined
- **THEN** only attributes listed in `__all__` are documented by default

### Requirement: Default Value Handling
The system SHALL allow controlling how default values are documented via `Default` metadata.

Priority: Medium

#### Scenario: Suppress Default Value
- **WHEN** an argument has `Default(mode=ValuationModes.Suppress)`
- **THEN** the default value is omitted from the generated documentation

#### Scenario: Surrogate Default Value
- **WHEN** an argument has `Default(mode=ValuationModes.Surrogate, surrogate="value")`
- **THEN** "value" is shown as the default in the documentation

### Requirement: Decoration Safety
The system SHALL prevent multiple decoration of the same object and ensure minimal overhead.

Priority: Critical

#### Scenario: Multiple Decoration Prevention
- **WHEN** an object is decorated multiple times
- **THEN** it is processed only once (idempotency)

### Requirement: Sphinx Compatibility
Generated docstrings SHALL be compatible with Sphinx Autodoc.

Priority: Critical

#### Scenario: Sphinx Parsing
- **WHEN** generated docstrings are parsed by Sphinx
- **THEN** they render correctly without syntax errors
