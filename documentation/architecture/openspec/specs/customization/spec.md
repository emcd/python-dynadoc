# Customization

## Purpose
Provides extension points for users to customize the output format, manage reusable content, and configure the documentation generation process.

## Requirements

### Requirement: Custom Renderers
Custom renderers SHALL be capable of generating documentation in formats other than Sphinx reStructuredText.

Priority: High

#### Scenario: Renderer Protocol
- **WHEN** a custom renderer matching the `Renderer` protocol is provided
- **THEN** it receives introspection data and context
- **AND** its output is used as the generated docstring

### Requirement: Fragment Tables
Reusable documentation fragments SHALL be definable and referenced from multiple locations.

Priority: Medium

#### Scenario: Fragment Reference
- **WHEN** a string annotation matches a key in the `FragmentsTable`
- **THEN** the corresponding value from the table is used in the documentation

#### Scenario: Missing Fragment
- **WHEN** a fragment name is not found in the table
- **THEN** an error is reported via the notifier

### Requirement: Context Configuration
`Context` objects SHALL configure and customize the documentation generation process.

Priority: High

#### Scenario: Context Customization
- **WHEN** `produce_context()` is called with custom components (notifier, rectifier)
- **THEN** a `Context` object is created with those customizations
- **AND** the context is immutable to prevent accidental modification

### Requirement: Extension Protocols
The system SHALL provide protocols for custom components.

Priority: High

#### Scenario: Custom Implementation
- **WHEN** a user implements `Renderer`, `Notifier`, `VisibilityDecider`, or `FragmentRectifier` protocols
- **THEN** the system accepts and uses the custom implementation
