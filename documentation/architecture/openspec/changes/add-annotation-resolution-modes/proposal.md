# Change: Add Annotation Resolution Modes

## Why

Dynadoc currently accepts annotations as-is, including unresolved `ForwardRef`
objects and stringified annotations. This limits documentation quality for
codebases using forward references or string annotations. A configurable
resolution mode would enable stricter validation and richer documentation
extraction.

## What Changes

- Add `ResolutionMode` enum with `STRICT`, `ACCEPT`, and `PARSE` modes
- Integrate `typing_extensions.evaluate_forward_ref` for ForwardRef resolution
- Enhance `_access_annotations` with better error handling and namespace inference
- Add configurable fallback behavior when resolution fails

## Impact

- Affected specs: `annotation-extraction`, `introspection`
- Affected code: `introspection.py`, `context.py`, `interfaces.py`
