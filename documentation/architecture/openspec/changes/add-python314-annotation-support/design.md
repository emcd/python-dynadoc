## Context

Dynadoc needs to handle forward references in type annotations across all
supported Python versions (3.10+). Python 3.14 introduces PEP 649 lazy
annotation evaluation with new `__annotate__` descriptor and `annotationlib`
module. However, `typing_extensions` 4.13.0+ provides backports of the key
features we need, allowing us to support FORWARDREF format on older Python
versions.

## Goals / Non-Goals

**Goals:**
- Support forward references consistently across Python 3.10-3.14+
- Use `typing_extensions.get_annotations` with FORWARDREF format when available
- Use `typing_extensions.evaluate_forward_ref` for ForwardRef resolution
- Maintain backward compatibility when typing_extensions < 4.13.0

**Non-Goals:**
- Drop support for Python 3.10-3.13
- Require typing_extensions (it's already a dependency, but we handle absence)
- Implement full SOURCE format support (can be added later)

## Decisions

### Decision: Use typing_extensions as primary mechanism

**What:** Use `typing_extensions.get_annotations(obj, format=Format.FORWARDREF)`
as the primary annotation access method when typing_extensions >= 4.13.0 is
available.

**Why:** This provides consistent FORWARDREF behavior across all supported
Python versions (3.10+), not just 3.14+. The typing_extensions backport
provides a "rough approximation" of PEP 649 behavior on older Python.

**Alternatives considered:**
1. Use `inspect.get_annotations` with format on 3.14+, fall back to custom
   logic on older versions — Rejected because it requires maintaining two
   separate code paths
2. Use `annotationlib` directly on 3.14+ — Rejected because annotationlib
   has no backport and only works on 3.14+

### Decision: Fallback strategy for older typing_extensions

**What:** Require `typing-extensions >= 4.13.0` in pyproject.toml. No fallback
logic for older versions.

**Why:** Simplifies code by eliminating version detection and fallback paths.
typing-extensions is already a dependency; bumping the minimum version is
straightforward. Users can easily upgrade typing-extensions.

**Alternatives considered:**
1. Support older typing-extensions with fallback logic — Rejected because it
   adds code complexity and maintenance burden

### Decision: Integrate evaluate_forward_ref for ForwardRef processing

**What:** Use `typing_extensions.evaluate_forward_ref()` to resolve ForwardRef
objects when available, falling back to existing logic otherwise.

**Why:** This function recursively evaluates nested forward references and
handles None → NoneType conversion, providing better documentation quality.

## Risks / Trade-offs

- **Risk:** typing_extensions FORWARDREF format is a "rough approximation"
  — **Mitigation:** Test thoroughly with real-world codebases; document
  limitations
- **Risk:** Version detection complexity — **Mitigation:** Use feature
  detection (try/except) rather than version checking
- **Risk:** Performance impact from additional typing_extensions calls
  — **Mitigation:** Cache annotation access; only call when needed

## Migration Plan

1. Add typing_extensions >= 4.13.0 as optional dependency (already present)
2. Update `_access_annotations` to use typing_extensions when available
3. Add feature detection for `evaluate_forward_ref`
4. Test with Python 3.10, 3.12, 3.14 and typing_extensions 4.12, 4.13+
5. Update documentation with new ResolutionMode options

## Open Questions

### Should we add a ResolutionMode specifically for FORWARDREF format?

**Recommendation:** No. With `typing-extensions >= 4.13.0` required, FORWARDREF
should be the default behavior for ACCEPT mode. Users get better forward
reference handling automatically. STRICT mode remains useful for users who
want warnings about unresolved references. No new mode needed.

### How should we handle complex forward references that don't resolve?

**Recommendation:** Follow the existing proposal's design:
- **ACCEPT mode**: Silently use the `__forward_arg__` string (expected behavior)
- **STRICT mode**: Issue a warning via notifier, then use the string

This is consistent with how the modes are already defined and avoids
surprising users with warnings in the default mode.

### Should SOURCE format be a separate feature, or part of ResolutionMode?

**Recommendation:** Separate. SOURCE format (returning annotations as source
code strings) is orthogonal to how we handle forward references:
- **ResolutionMode** controls processing behavior (strict/accept/parse)
- **SOURCE format** controls representation (evaluated values vs source strings)

Add SOURCE format as a configuration option in `IntrospectionControl`,
independent of ResolutionMode. This allows combining SOURCE format with any
mode (e.g., SOURCE + STRICT for documentation with strict validation).
