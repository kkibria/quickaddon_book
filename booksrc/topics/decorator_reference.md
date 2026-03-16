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
    param_subtypes={"cache_dir": "DIR_PATH"},
    inject={"ctx": "ctx"},
)
def setup_from_audio(audio_path: Path, bpm: int = 120, cache_dir: str = "", ctx: Any = None):
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
| `param_subtypes` | Overrides generated Blender property subtypes |
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

Runtime contract:

* `pathlib.Path` parameters are passed to user code as `Path` objects
* `str` parameters are passed to user code as plain strings
* `param_subtypes` affects Blender UI only, not runtime conversion

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

## Panel

`panel` controls whether QuickAddon includes the operator in its auto-generated
panel UI.

- `panel=True`
  - Generate and register the operator
  - Include it in the generated panel tool list
- `panel=False`
  - Generate and register the operator
  - Do not include it in the generated panel tool list

This is a UI composition flag only.

It does **not**:

- remove the operator
- disable the operator
- remove parameters
- prevent invocation from other UI or code

An operator with `panel=False` still exists as a normal Blender operator and can be
invoked by `bl_idname` from menus, custom panels, keymaps, scripts, or host add-ons.

### Why This Exists

Most QuickAddon examples start with the default generated panel because that is the
lowest-friction path.

But QuickAddon supports a broader set of UI patterns:

- standard panel-first tools
- menu-driven operators
- host-composed tools drawn by another add-on
- hidden helper operators used for workflow plumbing

`panel` is what lets one generated operator model support all of those cases.

### Menu Behavior

`panel=False` is a good fit for menu-only operators.

If the operator has local parameters:

- invoking it from a menu still opens Blender's floating properties dialog
- the user can enter values before execution

If the operator has no local parameters:

- it runs immediately when invoked

Shared parameters are different:

- shared values do not appear in the local popup dialog
- shared values are expected to be drawn by host/shared UI instead

### Interaction With `shared`

`panel=False` can be used with `shared`, but only when some other UI is responsible
for exposing those shared values.

Good fit:

- a host add-on panel already draws the shared inputs
- a custom UI calls generated draw helpers
- shared values are owned by a host integration layer

Awkward fit:

- the generated QuickAddon panel was the only place users could edit those shared values

Practical rule:

- `panel=False + shared` is useful when another UI surface owns the shared state
- `panel=False + shared` is confusing when no other UI exists for those shared inputs

### Mental Model

`panel` answers one question:

> Should QuickAddon auto-surface this operator in its default panel UI?

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

## `param_subtypes`

Use `param_subtypes` when you want filepath-style Blender UI without changing the
runtime Python type:

```python
@op(
    param_subtypes={
        "json_path": "FILE_PATH",
        "cache_dir": "DIR_PATH",
    }
)
def export_transforms(json_path: str = "", cache_dir: str = ""):
    ...
```

Rules:

* Supported values are currently `"FILE_PATH"` and `"DIR_PATH"`.
* Valid only for `str` and `Path` parameters.
* For `Path`, QuickAddon still passes a `Path` object at runtime.
* For `str`, QuickAddon still passes a plain string at runtime.

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
