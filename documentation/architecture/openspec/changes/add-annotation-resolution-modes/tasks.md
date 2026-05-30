# Implementation Tasks

## 1. Core Infrastructure

- [ ] 1.1 Create `ResolutionMode` enum in `interfaces.py` (STRICT, ACCEPT)
- [ ] 1.2 Add `resolution_mode` field to `IntrospectionControl` dataclass
- [ ] 1.3 Define error/warning types for resolution failures

## 2. STRICT Mode Implementation

- [ ] 2.1 Add detection for unresolved `ForwardRef` objects
- [ ] 2.2 Add detection for string annotations
- [ ] 2.3 Implement notifier integration for resolution failures
- [ ] 2.4 Add tests for STRICT mode behavior

## 3. ACCEPT Mode with FORWARDREF

- [ ] 3.1 Use `typing_extensions.get_annotations` with FORWARDREF format
- [ ] 3.2 Integrate `typing_extensions.evaluate_forward_ref` for ForwardRef processing
- [ ] 3.3 Add configurable globals/locals for evaluation context
- [ ] 3.4 Implement graceful handling when ForwardRef cannot be resolved
- [ ] 3.5 Add tests for ACCEPT mode with forward references

## 4. Documentation

- [ ] 4.1 Update architecture docs with resolution mode details
- [ ] 4.2 Add examples showing STRICT vs ACCEPT mode behavior
- [ ] 4.3 Document migration path for existing codebases

## 5. Deferred

- [ ] 5.1 PARSE mode (AST-based string annotation parsing) — future enhancement
