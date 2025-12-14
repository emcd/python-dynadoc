# Introspection

## Purpose
Controls the scope and depth of documentation generation, allowing users to define what gets documented and how visibility rules are applied.

## Requirements

### Requirement: Visibility Control
Attribute visibility SHALL be controlled to hide internal implementation details or force documentation of specific members.

Priority: High

#### Scenario: Conceal Visibility
- **WHEN** an attribute has `Visibilities.Conceal` annotation
- **THEN** it is excluded from the generated documentation

#### Scenario: Reveal Visibility
- **WHEN** an attribute has `Visibilities.Reveal` annotation
- **THEN** it is included in the generated documentation even if private

#### Scenario: Custom Visibility Decider
- **WHEN** a custom `VisibilityDecider` is provided in the context
- **THEN** it determines visibility based on the possessor, name, and annotation

### Requirement: Introspection Control
Introspection configuration SHALL control which object types are recursively documented and the documentation scope.

Priority: Medium

#### Scenario: Target Selection
- **WHEN** `IntrospectionControl.targets` includes `Module`
- **THEN** submodules matching the package prefix are recursively documented

#### Scenario: Recursion Limit
- **WHEN** an object defines `_dynadoc_introspection_limit_`
- **THEN** recursion depth and targets are limited for that object's subtree

### Requirement: Custom Introspectors
The system SHALL support custom introspectors for special class types.

Priority: Medium

#### Scenario: Special Class Introspection
- **WHEN** a class has special structure (e.g., Enum, dataclass)
- **THEN** a registered custom introspector can handle it
