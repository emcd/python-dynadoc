# TODO Items for dynadoc

## Annotation Resolution Enhancements

### 1. Leverage `typing_extensions.evaluate_forward_ref` (v4.13.0+)

The new `evaluate_forward_ref` function provides sophisticated ForwardRef evaluation:
- Recursively evaluates nested forward references
- Validates type hint correctness  
- Handles `None` → `types.NoneType` conversion
- Supports explicit `globals`/`locals` namespaces

**Current state**: We extract `__forward_arg__` strings from ForwardRef objects
**Enhancement**: Use `evaluate_forward_ref` to actually resolve references when possible

**Implementation notes**:
- Would fit into new `resolution_mode` framework (see below)
- Could significantly improve documentation quality for forward references
- Need to handle evaluation failures gracefully

### 2. Add `resolution_mode` Control Attribute

Introduce an enum-based control for annotation processing behavior:

```python
class ResolutionMode(enum.Enum):
    STRICT = "strict"    # All annotations must be fully resolved
    ACCEPT = "accept"    # Current behavior: accept as-is  
    PARSE = "parse"      # Attempt parsing and resolution
```

**STRICT mode**:
- Reject stringified annotations and unresolved ForwardRefs
- Useful for modern codebases wanting strict type validation
- Implementation: raise errors/warnings via notifier for unresolved types

**ACCEPT mode** (current default):
- Maintain existing behavior for compatibility
- Pass through strings and ForwardRef.__forward_arg__ as-is

**PARSE mode** (most ambitious):
- Parse annotation strings using Python AST/tokenizer
- Attempt resolution via inferred/supplied globals/locals  
- Extract metadata from `Annotated` types even when base type is stringified
- Enable rich documentation from legacy stringified annotations

**Migration path**: Start with STRICT → enhance ACCEPT → implement PARSE

### 3. Improve `_access_annotations` Function

**Current TODOs from code**:
- Consider using `eval_str=True` parameter again with better error handling
- Investigate performance implications of default vs explicit annotation resolution
- Add more sophisticated namespace inference for evaluation

**Related enhancements**:
- Better error messages for annotation resolution failures
- Configurable fallback behavior when resolution fails
- Support for custom evaluation contexts per possessor type

## Implementation Priority

1. **High**: Create `ResolutionMode` enum and basic STRICT mode
2. **High**: Integrate `evaluate_forward_ref` for ForwardRef resolution  
3. **Medium**: Enhanced error handling and namespace inference
4. **Low**: Full PARSE mode with AST-based string parsing

## Python 3.14 Lazy Annotation Evaluation

### Investigation Needed: `__annotate__` and `annotationslib` Support

Python 3.14 introduces PEP 649 lazy evaluation of annotations:
- **`__annotate__` method**: Replaces `__annotations__` dict for lazy evaluation
- **`annotationslib` module**: Provides `get_annotations()` and related utilities
- **Impact**: May affect how Dynadoc introspects and processes type annotations

**Questions to investigate**:
1. Does our current `_access_annotations` function handle `__annotate__` correctly?
2. Should we use `annotationslib.get_annotations()` when available (Python 3.14+)?
3. How does lazy evaluation interact with our annotation reduction pipeline?
4. Are there performance implications or opportunities with lazy evaluation?
5. Do we need special handling for the evaluation context/namespace?

**References**:
- PEP 649: Deferred Evaluation of Annotations
- Python 3.14 `annotationslib` documentation
- Interaction with PEP 727 `Doc` objects

**Priority**: Medium - Should investigate before promoting Python 3.14 support beyond testing

## Notes

- `evaluate_forward_ref` requires `typing_extensions>=4.13.0`
- PARSE mode could be a significant differentiator for dynadoc
- Consider backward compatibility when changing default behaviors
- Document performance implications of different resolution modes