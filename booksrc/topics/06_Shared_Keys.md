---

title: Host Ownership of Shared Values

---

# {{ page.title }}



In the previous chapter:

* `audiodeck` became the host.
* `audio_encode` was embedded inside it.
* The UI was unified.
* Only `audiodeck` was enabled.

However, one important thing has **not** changed yet.

`audio_encode` is still storing its shared values in fallback storage.

---

## Current State

Right now, shared values for `audio_encode` live in:

```text id="oqexxk"
context.scene.qa_shared
```

So even though:

* `audiodeck` controls the panel
* `audio_encode` renders inside it

The data is still owned by generated fallback storage.

> `audiodeck` controls the UI, but not the data.

---

## Why This Matters

Suppose `audiodeck` already defines its own property group:

```python id="qz91md"
class AudioDeckProps(bpy.types.PropertyGroup):
    audio_path: bpy.props.StringProperty(
        name="Audio Path",
        subtype="FILE_PATH"
    )
```

And suppose it is registered as:

```python id="qykpcc"
bpy.types.Scene.audiodeck_props = bpy.props.PointerProperty(
    type=AudioDeckProps
)
```

Now we have two places storing the same concept:

```text id="3ntpmp"
context.scene.audiodeck_props.audio_path
context.scene.qa_shared.project__audio_path
```

Two values.
One meaning.

That duplication is unnecessary.

If `audiodeck` is the host, it should own the data.

---

## The Mechanism: HostAPI

When `audio_encode` reads or draws a shared value, it does **not** directly access storage.

Instead, it calls:

```python id="7ekp3r"
host_api.get(...)
host_api.draw(...)
```

Until now, we were relying on the default fallback host.

Now we will provide our own.

---

## Step 1 – Implement a Minimal HostAPI in `audiodeck`

Open:

```text id="v6ylxj"
audiodeck/__init__.py
```

Add the following class:

```python id="9cskv1"
class AudioDeckHostAPI:

    def get(self, context, key, fallback_prop):
        if key == "project.audio_path":
            return context.scene.audiodeck_props.audio_path

        # fallback for unknown keys
        return getattr(context.scene.qa_shared, fallback_prop)

    def draw(self, layout, context, key, fallback_prop, label=None):
        if key == "project.audio_path":
            layout.prop(
                context.scene.audiodeck_props,
                "audio_path",
                text=label
            )
        else:
            layout.prop(
                context.scene.qa_shared,
                fallback_prop,
                text=label
            )
```

This class does two things:

* Routes `"project.audio_path"` into `audiodeck_props`.
* Falls back to generated storage for all other shared keys.

The plugin does not change.
Only the host’s routing logic changes.

---

## Step 2 – Inject the HostAPI

Modify the registration of `audio_encode` inside `audiodeck.register()`:

```python id="5uf1vt"
audio_encode_ops.register(
    mode="plugin",
    host_api=AudioDeckHostAPI()
)
```

That is the entire ownership transfer.

---

## What Changed?

Before:

```text id="0g6l0g"
audio_encode
    └── qa_shared
```

After:

```text id="8kux8x"
audio_encode
    └── HostAPI
          └── audiodeck_props
```

Now:

* `audio_encode` reads from `audiodeck` storage.
* `audio_encode` draws `audiodeck` properties.
* Fallback storage remains available for other shared keys.

---

## What Did NOT Change

* `audio_encode` tool script
* `audio_encode` shared decorator
* `audio_encode` operator logic
* `audio_encode` build process

Only `audiodeck` changed.

The plugin remains generated, reusable, and composable.

---

## What You Have Now

At this point:

* UI ownership belongs to `audiodeck`.
* Data ownership belongs to `audiodeck`.
* `audio_encode` remains independent and reusable.
* The relationship is defined entirely through the HostAPI contract.

In the next chapter, we will make this routing scalable — so you do not have to write `if key == ...` for every shared value.
