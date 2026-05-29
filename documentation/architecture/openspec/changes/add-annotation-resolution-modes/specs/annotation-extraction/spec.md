## ADDED Requirements

### Requirement: Resolution Mode Control

The system SHALL provide a configurable resolution mode that controls how
annotations are processed, particularly for forward references and string
annotations.

Priority: High

#### Scenario: STRICT Mode Rejects Unresolved References
- **WHEN** resolution mode is set to `STRICT`
- **AND** an annotation contains an unresolved `ForwardRef` or string annotation
- **THEN** a warning is issued via the notifier
- **AND** the annotation is documented with its unresolved form

#### Scenario: ACCEPT Mode Preserves Current Behavior
- **WHEN** resolution mode is set to `ACCEPT` (default)
- **THEN** annotations are processed as-is, preserving backward compatibility
- **AND** `ForwardRef` objects are documented using their `__forward_arg__` string

#### Scenario: Enhanced ACCEPT Mode Attempts Resolution
- **WHEN** resolution mode is set to `ACCEPT`
- **AND** `typing_extensions.evaluate_forward_ref` is available
- **THEN** the system attempts to resolve forward references
- **AND** resolution failures fall back to documenting the unresolved form

### Requirement: Forward Reference Resolution

The system SHALL attempt to resolve forward references using available
evaluation context when configured to do so.

Priority: High

#### Scenario: Successful Resolution
- **WHEN** a `ForwardRef` can be resolved using available globals/locals
- **THEN** the resolved type is used for documentation generation
- **AND** the documentation reflects the actual type rather than the reference string

#### Scenario: Resolution Failure Handling
- **WHEN** a `ForwardRef` cannot be resolved
- **AND** resolution mode is `ACCEPT`
- **THEN** a warning is issued via the notifier
- **AND** the forward reference string is used as fallback documentation

#### Scenario: Custom Evaluation Context
- **WHEN** custom globals or locals are provided via `IntrospectionControl`
- **THEN** the custom context is used for forward reference evaluation
- **AND** the custom context takes precedence over inferred context
