# Change: Investigate Python 3.14 Lazy Annotation Evaluation

## Why

Python 3.14 introduces PEP 649 lazy evaluation of annotations via the
`__annotate__` method and `annotationslib` module. This change may affect
how Dynadoc introspects and processes type annotations. We need to investigate
the impact and ensure compatibility before promoting Python 3.14 support
beyond testing.

## What Changes

- Investigate `__annotate__` method behavior and compatibility
- Evaluate `annotationslib.get_annotations()` for Python 3.14+
- Assess impact on annotation reduction pipeline
- Determine performance implications of lazy evaluation
- Document findings and recommended approach

## Impact

- Affected specs: `annotation-extraction`, `introspection`
- Affected code: `introspection.py` (annotation access logic)
- Python version support: 3.14+ (when available)
