---
title: Injection Contract v1
---


# {{ page.title }}
The Injection Contract defines how runtime values (such as Blender context)
are passed into plugin functions.

This system is separate from HostAPI and shared key routing.

HostAPI handles shared state.
Injection handles runtime wiring.

---

## Core Principle

Injection is **explicit**.

Nothing is auto-wired.

A parameter is injected only if it is declared in:

```python
@op(inject={ ... })
```

---

## Basic Usage

```python
from typing import Any

@op(
    label="Example",
    inject={
        "ctx": "ctx",
        "scene": "scene",
    },
)
def example(ctx: Any, scene: Any, threshold: float = 0.5):
    ...
```

Parameters listed in `inject`:

* Do not generate UI fields.
* Are passed at operator execution time.
* Must match function parameter names.

---

## Injection Mapping

Injection is defined as:

```python
inject={
    "parameter_name": "expression_or_alias",
}
```

The right-hand side may be:

### 1) Full Expression

Evaluated relative to `execute(self, context)` scope.

Example:

```python
inject={
    "ctx": "context",
    "active_strip": "context.scene.sequence_editor.active_strip",
}
```

This generates static wiring:

```python
ctx=context
active_strip=context.scene.sequence_editor.active_strip
```

No dynamic `eval` is used at runtime.

---

### 2) Built-in Aliases

These aliases expand to common context values:

| Alias    | Expands To               |
| -------- | ------------------------ |
| `ctx`    | `context`                |
| `scene`  | `context.scene`          |
| `wm`     | `context.window_manager` |
| `area`   | `context.area`           |
| `region` | `context.region`         |
| `space`  | `context.space_data`     |

Example:

```python
inject={
    "ctx": "ctx",
}
```

Expands to:

```python
ctx=context
```

---

## Strictness Rules

### 1) Injection Must Be Explicit

There is no automatic context injection.

Even though operators receive `context`,
it must be declared if used.

---

### 2) `Any` Requires Injection

If a parameter:

* Is annotated as `Any`
* Has no default value
* Is not declared in `inject`

Build fails.

Example error:

```
Parameter 'ctx' is annotated as Any but not declared in @op(inject=...).
Injection must be explicit.
```

This prevents accidental UI generation or ambiguous wiring.

---

### 3) Unknown Alias Is an Error

If injection value is:

* Not a built-in alias
* Not a valid expression

Build fails.

No guessing.
No silent fallback.

---

## Runtime Behavior

If an injected expression evaluates to `None`,
the function receives `None`.

Example:

* `context.area` may be `None`
* `context.scene.sequence_editor` may be `None`

Handling `None` is the responsibility of the plugin author.

---

## Design Philosophy

Injection exists to support:

* Context-aware operators
* Refactoring existing addons
* Future extension beyond Blender context

It does not:

* Replace shared keys
* Replace HostAPI
* Imply ownership of runtime state

---

## Relationship to HostAPI

HostAPI:

* Routes shared keys.
* Manages persistent state.

Injection:

* Supplies runtime values.
* Has no persistence semantics.

The two systems are orthogonal by design.
