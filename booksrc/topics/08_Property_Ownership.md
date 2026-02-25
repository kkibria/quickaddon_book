---

title: Property Ownership – A Clean Routing Pattern

---

# {{ page.title }}



In the previous chapter, we formalized the HostAPI contract.

We saw that:

* Plugins speak in shared keys.
* Hosts decide where those keys live.
* Routing happens through `get()` and `draw()`.

Earlier, we implemented routing using:

```python
if key == "project.audio_path":
    ...
```

That works for one key.

It does not scale.

This chapter introduces a clean, declarative routing pattern.

---

## The Problem with `if` Chains

Suppose `audio_encode` defines three shared keys:

```python
shared={
    "audio_path": "project.audio_path",
    "bpm": "project.bpm",
    "output_dir": "project.output_dir",
}
```

Writing:

```python
if key == ...
elif key == ...
elif key == ...
```

Becomes repetitive and fragile.

As the number of shared keys grows, branching logic becomes harder to reason about and maintain.

We want:

* Explicit mapping
* Easy extension
* No branching logic explosion
* Clear ownership declaration

---

## Step 1 – Define a KEYMAP

Inside `audiodeck/__init__.py`:

```python
KEYMAP = {
    "project.audio_path": ("audiodeck_props", "audio_path"),
    "project.bpm": ("audiodeck_props", "bpm"),
    "project.output_dir": ("audiodeck_props", "output_dir"),
}
```

Each entry maps:

```text
shared_key → (property_group_name, attribute_name)
```

This makes ownership explicit and declarative.

The host now clearly states:

> “These shared keys belong to these properties.”

---

## Step 2 – Refactor HostAPI to Use KEYMAP

Replace the earlier implementation with:

```python
class AudioDeckHostAPI:

    def get(self, context, key, fallback_prop):
        if key in KEYMAP:
            group_name, attr = KEYMAP[key]
            group = getattr(context.scene, group_name)
            return getattr(group, attr)

        return getattr(context.scene.qa_shared, fallback_prop)

    def draw(self, layout, context, key, fallback_prop, label=None):
        if key in KEYMAP:
            group_name, attr = KEYMAP[key]
            group = getattr(context.scene, group_name)
            layout.prop(group, attr, text=label)
        else:
            layout.prop(
                context.scene.qa_shared,
                fallback_prop,
                text=label
            )
```

Routing is now centralized.

No condition chains.
No duplication.
No hidden logic.

---

## Adding a New Shared Key

To route a new key, modify only the KEYMAP:

```python
KEYMAP["project.sample_rate"] = ("audiodeck_props", "sample_rate")
```

No other code changes are required.

Growth becomes mechanical.

---

## Fallback Still Works

If a shared key is not listed in KEYMAP:

* It automatically uses fallback storage.
* The plugin continues to function.
* Ownership transfer can be incremental.

This makes adoption safe and predictable.

---

## Discipline Guidelines

To keep routing reliable:

* Shared keys must match exactly.
* Host property types must match plugin expectations.
* Avoid transforming values inside HostAPI.
* Keep KEYMAP static and explicit.

HostAPI is a routing layer.
It should remain simple.

---

## What You Now Have

At this point:

* UI ownership belongs to `audiodeck`.
* Data ownership belongs to `audiodeck`.
* Routing is scalable.
* Fallback behavior is preserved.
* Plugins remain reusable.

In the next chapter, we extend this model to multiple embedded plugins.
