---

title: QuickAddon HostAPI v2 Spec

---

# {{ page.title }}

HostAPI v2 introduces **scoped named instances** and enables:

* Multi-instance plugins
* Nested composition (host-of-host)
* Isolated storage per plugin instance
* Hierarchical system construction

HostAPI v2 replaces the single-instance model of v1.

> v1 and v2 are separate build tracks.

---

## Core Concepts

### Scope

A **scope** represents one logical instance of a plugin within a host.

Each mounted plugin instance receives a unique scope.

All shared key routing happens inside that scope.

Shared keys are no longer resolved globally.
They are resolved as:

```

(scope, key)

```

Scope identity is:

* Host-defined
* Opaque to plugins
* Stable across file save/load
* Unique within a scene

Plugins must not assume scope format.

---

### Bound HostAPI

HostAPI v2 introduces `bind()`.

`bind()` allocates (or selects) a scope and returns a HostAPI instance bound to that scope.

After binding, all `get()` and `draw()` calls operate within that scope.

Scope allocation may be:

* **Eager** (during bind)
* **Lazy** (during first get/draw call)

Blender registration does not always provide reliable context,
so hosts may defer scope materialization until runtime.

Scope identity remains host-defined and opaque.

---

## Required Methods

```python
class HostAPI:

    def bind(
        self,
        context=None,
        instance_hint: str | None = None,
    ) -> "HostAPI":
        """
        Allocate (or select) a scope for this plugin instance.
        - `instance_hint` may be used to request deterministic naming
          (e.g., "encode_A").
        - `context` may be None; hosts may allocate lazily.
        - Returns a HostAPI bound to that scope.
        """
        ...

    def get(self, context, key: str, fallback_prop: str):
        """
        Return the value for shared key within this scope.

        `fallback_prop` remains the plugin-generated property
        name for fallback storage.
        """
        ...

    def draw(
        self,
        layout,
        context,
        key: str,
        fallback_prop: str,
        *,
        label: str | None = None,
    ):
        """
        Draw UI control for shared key within this scope.

        Must draw either:
        - a host-owned property
        - or a scoped fallback property
        """
        ...
```

These methods define the routing contract for v2.

`bind()` is a host/runtime mechanic.
Generated plugin users should think in terms of explicit named instances via
`mount_instance("name")`, not direct `bind()` calls.

---

## Public v2 Plugin Pattern

Generated v2 plugins expose a small explicit public pattern:

```python
plugin.register(host_api=host_api)
plugin.mount_instance("main")
plugin.unmount_instance("main")
plugin.unregister()
```

Rules:

* `register()` prepares the hosted runtime only.
* `register()` does **not** create a hidden default instance.
* Every usable instance is explicit and named.
* Internal instance keys remain opaque runtime details.
* Hosts should not call generated draw helpers directly.

---

## Scope Allocation Rules

* Each call to `bind()` allocates or selects one scope.
* Scope identifiers must be unique within a scene.
* Scope lifetime is tied to scene data.
* Scope identity must remain stable across file save/load.

Hosts may choose:

* Deterministic scope naming (recommended when the mounted instance has a stable name)
* Opaque auto-generated identifiers

Plugins must treat scope identity as opaque.

---

## Storage Model

HostAPI v2 does not mandate a specific storage backend.

Recommended fallback backend:

```
scene["qa_scope:<scope_id>:<fallback_prop>"]
```

IDProperties are recommended for:

* Arbitrary shared keys
* Multi-instance support
* Nested composition
* Dynamic routing

Hosts may route specific `(scope, key)` pairs to typed `PropertyGroup`s via KEYMAP.

---

## KEYMAP v2 Structure

KEYMAP must become scope-aware.

Hosts may implement either:

### Global Routing

```python
KEYMAP_GLOBAL = {
    "project.audio_path": ("audiodeck_props", "audio_path"),
}
```

### Scoped Override

```python
KEYMAP_SCOPED = {
    "<scope_id>": {
        "project.bpm": ("audiodeck_props", "bpm"),
    }
}
```

Resolution order for `get()`:

1. Scoped override `(scope_id, key)`
2. Global routing `key`
3. Scoped fallback storage

Isolation is enforced by design.

---

## Nested Composition

HostAPI v2 enables nested systems.

Example:

* Host A embeds Host B.
* Host A mounts a root plugin instance.
* Host-owned storage remains the ground for that tree.
* Parent nodes may later mount child nodes on top of the same scoped storage model.

Scopes may be hierarchical internally,
but hierarchy is an implementation detail of the host.

Plugins remain unaware of nesting.

---

## Plugin Responsibilities

Plugins in v2:

* Must not access `context.scene` directly for shared values
* Must use HostAPI for all shared key resolution
* May declare `long_task=True` (separate contract)
* Must remain stateless across scopes

Plugins declare intent.
Hosts enforce isolation.

---

## Host Responsibilities

Hosts in v2:

* Allocate scopes during registration or lazily at runtime
* Own scoped storage lifecycle
* Maintain scope-aware routing
* Enforce isolation between instances
* Optionally expose instance management UI

The host owns identity, routing, and lifecycle.

---

## Multi-Instance Behavior

The same plugin module may expose multiple mounted named instances.

Each mounted instance receives a distinct scope.

Shared keys are isolated per scope unless
explicitly routed by the host.

Isolation is the default.

---

## Instance Identity

Host-facing identity is instance-oriented.

Use explicit instance names when you need deterministic labels or grouping in host UI.

Plugin identity remains internal to generated artifacts and is opaque to host APIs.

---

## Upgrade Model

v1 and v2 are separate build tracks.

Upgrade path:

* Regenerate the add-on with the v2 CLI option
* Plugins remain unchanged at the source level
* Decorator additions (if any) are minimal
* No runtime compatibility layer is provided

The tracks do not mix.

---

## Design Principles

HostAPI v2 is based on:

* Explicit scoping
* Explicit instance mounting
* Centralized routing
* Host-owned execution control
* Composability over convenience
* Stability over magic

HostAPI v2 enables QuickAddon to function as a
composable UI architecture framework — not merely
an add-on generator.
