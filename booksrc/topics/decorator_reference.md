---
title: Decorator Reference
---

# {{ page.title }}

This page documents the user-facing `@op(...)` contract.

It is a reference page, not a teaching chapter.

Use it when you need the current supported decorator surface in one place.

---

## Basic Shape

```python
@op(
    label="Setup From Audio",
    category="QuickAddon",
    space="SEQUENCE_EDITOR",
    region="UI",
    panel=True,
    long_task=False,
    shared={"audio_path": "project.audio_path"},
    param_labels={"audio_path": "Audio File"},
    param_order={"audio_path": 100, "bpm": 10},
    inject={"ctx": "ctx"},
)
def setup_from_audio(audio_path: Path, bpm: int = 120, ctx: Any = None):
    ...
```

---

## Core Decorator Fields

| Field | Meaning |
| --- | --- |
| `label` | UI label for the generated operator |
| `idname` | Optional Blender operator idname override |
| `description` | Optional operator description |
| `category` | Panel tab/category |
| `space` | Blender editor space |
| `region` | Blender region |
| `panel` | Whether to include the op in generated panel UI |
| `long_task` | Enables the long-task generator contract |
| `shared` | Declares shared key routing by parameter |
| `param_labels` | Overrides generated UI labels |
| `param_order` | Controls display order; higher values render first |
| `inject` | Explicit runtime injection mapping |

`v1` and `v2` both use the same decorator surface.

Track differences apply to generated runtime behavior, not to the decorator syntax itself.

---

## Supported Parameter Types

QuickAddon currently supports:

* `str`
* `int`
* `float`
* `bool`
* `pathlib.Path`
* `Literal["a", "b", ...]`

These generate:

* `StringProperty`
* `IntProperty`
* `FloatProperty`
* `BoolProperty`
* `StringProperty(subtype="FILE_PATH")`
* `EnumProperty`

Not supported:

* `*args`
* `**kwargs`

Unsupported parameter types fail build with QA10 diagnostics.

---

## Shared Keys

Shared values are declared by parameter name:

```python
@op(
    shared={
        "audio_path": "project.audio_path",
    }
)
def setup_from_audio(audio_path: Path):
    ...
```

Rules:

* Shared keys are stable opaque identifiers.
* The same shared key must keep one consistent type across all ops.
* Shared parameters do not appear as local popup dialog properties.
* Shared values are drawn in the shared inputs group instead.

If multiple ops use the same shared key, they reference the same logical shared value.

---

## UI Labels

Use `param_labels` to override display names:

```python
@op(
    param_labels={
        "audio_path": "Audio File",
        "start_frame": "Start Frame",
    }
)
```

This applies to:

* Generated local operator properties
* Shared input draw labels

If you do not supply `param_labels`, QuickAddon uses the parameter name.

### Label Collision Rule

Resolved UI labels must be unique within each displayed group.

That means:

* Local properties within one operator dialog must not collide
* Shared inputs within the shared inputs group must not collide

Duplicate labels fail build with QA10 diagnostics.

---

## UI Ordering

Use `param_order` to control property order:

```python
@op(
    param_order={
        "audio_path": 100,
        "bpm": 10,
        "debug": 0,
    }
)
```

Rules:

* Higher order values appear first
* Parameters with the same order are sorted deterministically by UI label, then name
* Applies to both local properties and shared inputs

If `param_order` is omitted, the default order value is `0`.

---

## Long Tasks

If `long_task=True`:

* The function must be a generator
* Async generators are not allowed
* Runtime yield payloads must include `progress` and `total`

For the full contract, see [Diagnostics and Contract Enforcement](errorreporting.md).

---

## Injection

Injection is explicit and separate from shared routing.

Use:

```python
@op(
    inject={
        "ctx": "ctx",
        "scene": "scene",
    }
)
```

Injected parameters:

* Do not generate UI fields
* Are supplied at execution time
* Must be declared explicitly

For the full injection contract, see [Injection Contract v1](injection_contract_v1.md).

---

## Strictness Notes

QuickAddon does not silently guess through decorator ambiguity.

Examples of build failures:

* Unknown parameter referenced in `shared`, `param_labels`, `param_order`, or `inject`
* Shared key type mismatch across ops
* Duplicate resolved labels within one UI group
* Invalid `long_task=True` contract

Reference pages for related contracts:

* [Injection Contract v1](injection_contract_v1.md)
* [QuickAddon HostAPI v2 Spec](hostapi_v2_spec.md)
* [v1 to v2 migration](migration.md)
* [Diagnostics and Contract Enforcement](errorreporting.md)
