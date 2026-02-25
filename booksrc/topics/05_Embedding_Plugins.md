---

title: Embedding Plugins

---

# {{ page.title }}


This is where we start assembling systems from our Lego pieces.

In the previous chapter, we generated and used `audiodeck`.

Now consider this situation:

* **audiodeck** was generated first.
* You enabled it. It works.
* Later, you generated **audio_encode**.
* It also works standalone.

Their functionality is related.

Now you want:

> **audio_encode** to appear inside **audiodeck**’s panel
> without enabling **audio_encode** separately.

We are staying entirely inside the QuickAddon ecosystem.
Let’s walk through the process.

---

## Step 1 – Start from Two Generated Add-ons

After building both, your add-ons directory looks like:

```text
.../scripts/addons/
├── audiodeck/
│   ├── __init__.py
│   └── generated_ops.py
└── audio_encode/
    ├── __init__.py
    └── generated_ops.py
```

Each add-on works independently in standalone mode.

---

## Step 2 – Embed `audio_encode` Inside `audiodeck`

We will embed `audio_encode` physically inside `audiodeck`.

Final layout:

```text
.../scripts/addons/
└── audiodeck/
    ├── __init__.py
    ├── generated_ops.py
    └── audio_encode/
        ├── __init__.py
        └── generated_ops.py
```

What changed?

* We moved `audio_encode/` inside `audiodeck/`.
* Blender now sees only `audiodeck` as an add-on to enable.

`audio_encode` becomes a module inside the host.

---

## Step 3 – Modify `audiodeck`

Open:

```text
audiodeck/__init__.py
```

### Add the import

```python
from .audio_encode import generated_ops as audio_encode_ops
```

---

### Update `register()`

Extend `register()`:

```python
def register():
    # audiodeck registration (already generated)
    ...

    # Register audio_encode in plugin mode
    audio_encode_ops.register(mode="plugin")
```

Update `unregister()` accordingly:

```python
def unregister():
    audio_encode_ops.unregister()

    # audiodeck unregister logic
    ...
```

Important:

We use `mode="plugin"`.

This means:

* `audio_encode` registers its operators.
* `audio_encode` registers its shared definitions.
* `audio_encode` does **not** create its own panel.

Even in the standalone case in the previous chapter, we used `mode="plugin"` — this is the default and most common mode.

> The other modes exist purely for QuickAddon author's debugging convenience.

---

### Update `audiodeck`’s Panel `draw()`

Inside `audiodeck`’s panel class:

```python
def draw(self, context):
    layout = self.layout

    layout.label(text="audiodeck")
    layout.separator()

    layout.label(text="audio_encode")
    audio_encode_ops.draw(layout, context, category="QuickAddon")
```

That is the entire integration layer.

No changes were made to `audio_encode` itself.

---

## Step 4 – Enable Only `audiodeck`

In Blender:

* Disable `audio_encode` (if it was previously enabled).
* Enable `audiodeck`.

Result:

* Only one panel appears (`audiodeck`).
* `audio_encode` buttons appear inside it.
* Shared inputs render correctly.
* `audio_encode` functions execute normally.

---

## What Just Happened

Standalone `audio_encode`:

```text
audio_encode __init__.py
    └── creates its own panel
```

Embedded `audio_encode`:

```text
audiodeck __init__.py
    ├── registers audio_encode (plugin mode)
    └── draws audio_encode UI inside its own panel
```

`audio_encode` still contains:

* Its operators
* Its shared keys
* Its generated plumbing

Only `audiodeck` now controls:

* Panel ownership
* UI composition

---

## What Has NOT Changed

* The `audio_encode` tool script
* Its shared key declarations
* Its operator logic
* Its build process

Embedding modifies only the host (`audiodeck`).

The plugin remains untouched.

---

## Where Are Shared Values Stored?

At this stage:

* `audio_encode` still uses its generated fallback storage.
* `audiodeck` does not yet own `audio_encode`’s shared values.

In the next chapter, we will transfer ownership.

That is where the HostAPI contract becomes visible.

---

You now understand:

* How two generated add-ons relate
* How one becomes the host
* How a plugin is physically embedded
* How registration is redirected
* How UI is delegated

Next, we will make `audiodeck` own `audio_encode`’s shared values.
