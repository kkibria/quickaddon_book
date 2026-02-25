---

title: HostAPI – The Routing Contract

---

# {{ page.title }}



In the previous chapter, we transferred shared value ownership from fallback storage into `audiodeck`.

We did this by injecting a `HostAPI` implementation.

Now we formalize what that means.

This chapter defines the HostAPI contract.

---

## Why HostAPI Exists

A generated plugin never directly accesses storage.

It does not read from:

```text
context.scene.qa_shared
```

It does not read from:

```text
context.scene.audiodeck_props
```

Instead, whenever a shared value is:

* Read
* Drawn in the UI

The plugin calls:

```python
host_api.get(context, key, fallback_prop)
host_api.draw(layout, context, key, fallback_prop, label=...)
```

The plugin speaks only in **shared keys**.

The host decides where those keys live.

That separation is the purpose of HostAPI.

---

## Core Terms

### Shared Key

A stable identifier defined in the plugin decorator:

```python
shared={"audio_path": "project.audio_path"}
```

The plugin only knows:

```text
"project.audio_path"
```

It does not know how that key is stored.

---

### Fallback Property

A generated property name derived from the shared key:

```text
project__audio_path
```

This exists so the plugin can function in standalone mode.

If the host does not serve a key, fallback storage is used.

---

## Required Methods

A HostAPI implementation must define:

```python
class HostAPI:

    def get(self, context, key: str, fallback_prop: str):
        """
        Return the value for shared key `key`.

        - `key` is the shared key (e.g. "project.audio_path")
        - `fallback_prop` is the generated fallback property name
        """
        ...

    def draw(self, layout, context, key: str, fallback_prop: str, *, label=None):
        """
        Draw the UI control for shared key `key`.

        Must draw something:
        - host-owned property
        - or fallback property
        """
        ...
```

These two methods form the entire routing contract.

Nothing else is required.

---

## Fallback Behavior

If a host does not serve a shared key:

```python
return getattr(context.scene.qa_shared, fallback_prop)
```

and

```python
layout.prop(context.scene.qa_shared, fallback_prop, text=label)
```

This ensures:

* Plugins remain functional without a host.
* Hosts can adopt routing incrementally.
* Shared ownership is optional, not mandatory.

Fallback is not a special case — it is part of the design.

---

## Injection Model

When embedding a plugin, the host injects its HostAPI:

```python
audio_encode_ops.register(
    mode="plugin",
    host_api=AudioDeckHostAPI()
)
```

The plugin never creates the HostAPI itself.

The host always controls:

* Whether a HostAPI is provided
* Which implementation is used

Control remains centralized.

---

## Design Discipline

HostAPI is:

* A routing layer
* Not a transformation layer
* Not a validation framework
* Not a business logic container

It should:

* Map keys to storage
* Draw the correct property
* Preserve fallback behavior

Nothing more.

---

## What HostAPI Is Not

HostAPI does not:

* Know which plugin requested a key
* Store plugin identity
* Mutate shared keys
* Enforce global state

It is intentionally minimal.

---

## Where We Are

At this point, you understand:

* Plugins declare shared keys.
* Plugins never access storage directly.
* Hosts inject HostAPI.
* HostAPI routes shared keys to storage.

In the next chapter, we will implement a clean and scalable routing pattern inside `audiodeck`.
