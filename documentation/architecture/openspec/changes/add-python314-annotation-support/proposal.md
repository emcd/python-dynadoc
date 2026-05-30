# Change: Add Python 3.14+ Annotation Support

## Why

Python 3.14 introduces PEP 649 lazy evaluation of annotations via `__annotate__`
and `annotationlib`. This fundamentally changes how annotations are accessed and
processed. Dynadoc must adapt to support both legacy (eager) and modern (lazy)
annotation semantics while maintaining backward compatibility with Python 3.10-3.13.

Key changes in Python 3.14:
- `__annotate__` is a descriptor/method that lazily computes annotations
- `__annotations__` is now a data descriptor that calls `__annotate__` on first access
- `inspect.get_annotations` supports new `format` parameter: VALUE (1), FORWARDREF (2), SOURCE (3)
- `annotationlib` module provides new utilities for working with annotations
- Forward references can now be represented as `ForwardRef` proxy objects

**Important:** While `annotationlib` is only available in Python 3.14+,
`typing_extensions` 4.13.0+ provides backports of the key features we need:

- `typing_extensions.get_annotations(obj, format=Format.FORWARDREF)` — Works on 3.10+
- `typing_extensions.evaluate_forward_ref()` — Evaluates ForwardRef objects
- `typing_extensions.Format` enum — VALUE, FORWARDREF, STRING formats

This means we can use FORWARDREF format for forward reference handling
across all supported Python versions (3.10+), not just 3.14+.

## What Changes

- Update `_access_annotations` to handle `__annotate__` descriptor
- Use `inspect.get_annotations` with appropriate `format` parameter
- Support FORWARDREF format for better forward reference handling
- Support SOURCE format for documentation use cases
- Handle lazy evaluation timing (annotations evaluated on first access)
- Maintain backward compatibility with Python 3.10-3.13

## Impact

- Affected specs: `annotation-extraction`, `introspection`
- Affected code: `introspection.py` (annotation access logic)
- Python version support: 3.10+ (with conditional logic for 3.14+)
