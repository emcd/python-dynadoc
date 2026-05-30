# Change: Add Annotation Resolution Modes

## Why

Dynadoc currently accepts annotations as-is, including unresolved `ForwardRef`
objects and stringified annotations. This limits documentation quality for
codebases using forward references or string annotations. A configurable
resolution mode would enable stricter validation and richer documentation
extraction.

With `typing-extensions >= 4.13.0` now required (see `add-python314-annotation-support`),
FORWARDREF format is always available. ACCEPT mode will use FORWARDREF format
by default, providing better forward reference handling automatically.

## What Changes

- Add `ResolutionMode` enum with `STRICT` and `ACCEPT` modes (PARSE deferred)
- ACCEPT mode uses `typing_extensions.get_annotations` with FORWARDREF format by default
- STRICT mode issues warnings for unresolved ForwardRef objects
- Integrate `typing_extensions.evaluate_forward_ref` for ForwardRef resolution
- Enhance `_access_annotations` with better error handling and namespace inference

## Impact

- Affected specs: `annotation-extraction`, `introspection`
- Affected code: `introspection.py`, `context.py`, `interfaces.py`
- Depends on: `add-python314-annotation-support`
