# Annotation Extraction

## Purpose
Extracts documentation and metadata from Python type annotations, enabling rich, inline documentation that is processed into standard docstring formats.

## Requirements

### Requirement: Doc Extraction
`Doc` objects embedded in `Annotated` types SHALL be extracted and used as documentation text.

Priority: Critical

#### Scenario: Single Doc Object
- **WHEN** an annotation is `Annotated[T, Doc("description")]`
- **THEN** "description" is extracted as the documentation text

#### Scenario: Multiple Doc Objects
- **WHEN** an annotation has multiple `Doc` objects
- **THEN** their contents are concatenated with proper spacing
- **AND** multiline descriptions are indented correctly

### Requirement: Raises Documentation
`Raises` annotations in return types SHALL document exceptions that may be raised.

Priority: Critical

#### Scenario: Single Exception
- **WHEN** the return annotation includes `Raises(ExceptionClass, "description")`
- **THEN** a `:raises ExceptionClass:` field is generated with the description

#### Scenario: Multiple Exceptions
- **WHEN** multiple `Raises` annotations are present
- **THEN** each is processed independently and added to the docstring

#### Scenario: Exception Sequence
- **WHEN** `Raises` is initialized with a sequence of exception classes
- **THEN** they are documented as a Union of exceptions

### Requirement: Complex Type Reduction
Complex generic types SHALL be reduced to a readable format for documentation.

Priority: High

#### Scenario: Union Types
- **WHEN** a type is `Union[A, B]` or `A | B`
- **THEN** it is rendered as `A | B` in the documentation

#### Scenario: Generic Types
- **WHEN** a type is `Container[ElementType]`
- **THEN** it is rendered with its generic arguments recursively reduced

#### Scenario: Forward References
- **WHEN** a type is a `ForwardRef` or string annotation
- **THEN** it is rendered as the string representation
- **AND** infinite recursion from cycles is prevented via cache

### Requirement: Cycle Detection
The system SHALL detect and handle reference cycles in annotations.

Priority: Critical

#### Scenario: Recursive Types
- **WHEN** a type definition refers to itself
- **THEN** infinite recursion is prevented
- **AND** the type is represented as `Any` or a string reference in documentation

### Requirement: Malformed Annotation Handling
The system SHALL handle invalid or malformed annotations gracefully.

Priority: High

#### Scenario: Invalid Metadata
- **WHEN** annotation metadata is invalid (e.g., non-Doc object where expected)
- **THEN** a warning is issued via the notifier
- **AND** the invalid metadata is dropped from processing
- **AND** the process continues without crashing
