---

title: QuickAddon HostAPI v2 Spec

---

# {{ page.title }}


HostAPI v2 introduces **scoped instances** and enables:

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

Each plugin registration receives a unique scope.

All shared key routing happens inside that scope.

Shared keys are no longer resolved globally.
They are resolved as:

```
(scope, key)
```

---

### Bound HostAPI

HostAPI v2 introduces `bind()`.

`bind()` allocates a scope and returns a HostAPI instance bound to that scope.

After binding, all `get()` and `draw()` calls operate within that scope.

Scope identity is host-defined and opaque to plugins.

---

## Required Methods

```python
class HostAPI:

    def bind(
        self,
        context,
        plugin_id: str,
        instance_hint: str | None = None,
    ) -> "HostAPI":
        """
        Allocate (or select) a scope for this plugin instance.

        - `plugin_id` identifies the registering plugin module.
        - `instance_hint` may be used to request deterministic naming
          (e.g., "encode_A").
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

---

## Scope Allocation Rules

* Each call to `bind()` allocates or selects one scope.
* Scopes must be unique within a scene.
* Scope identifiers are opaque and host-defined.
* Scope lifetime is tied to scene data.
* Scope identity must remain stable across file save/load.

Hosts may choose:

* Deterministic scope naming (recommended when `instance_hint` is provided)
* Opaque auto-generated identifiers

Plugins must not assume scope format.

---

## Storage Model

HostAPI v2 does not mandate a specific storage backend.

Recommended fallback backend:

```
scene["qa_scopes"][scope_id][fallback_prop]
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

Recommended structure:

```python
KEYMAP = {
    "<scope_id>": {
        "project.audio_path": ("audiodeck_props", "audio_path"),
        "project.bpm": ("audiodeck_props", "bpm"),
    }
}
```

Resolution order for `get()`:

1. If `(scope, key)` exists in KEYMAP → return host-owned value
2. Else → return scoped fallback storage

Isolation is enforced by design.

---

## Nested Composition

HostAPI v2 enables nested systems.

Example:

* Host A embeds Host B.
* Host A calls `bind()` to allocate a scope for B.
* Host A passes the bound HostAPI to B during registration.
* B allocates child scopes using its bound API.

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

* Allocate scopes during registration
* Own scoped storage lifecycle
* Maintain scope-aware KEYMAP
* Enforce isolation between instances
* Optionally expose instance management UI

The host owns identity, routing, and lifecycle.

---

## Multi-Instance Behavior

The same plugin module may be registered multiple times.

Each registration receives a distinct scope.

Shared keys are isolated per scope unless
explicitly routed by the host.

Isolation is the default.

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
* Centralized routing
* Host-owned execution control
* Composability over convenience
* Stability over magic

HostAPI v2 enables QuickAddon to function as a
composable UI architecture framework — not merely
an add-on generator.
