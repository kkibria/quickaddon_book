---

title: Refactoring Existing Addon into Plugin

---

# {{ page.title }}




In the previous chapter, we refactored an existing add-on into a host.

Now we take the opposite direction.

Instead of turning a legacy add-on into a host,
we turn it into a reusable plugin.

The goal is composability.

---

## The Starting Point

Consider a typical legacy operator:

```python id="lf4p90"
class AUDIO_OT_normalize(bpy.types.Operator):
    bl_idname = "audio.normalize"
    bl_label = "Normalize Audio"

    def execute(self, context):
        audio_path = context.scene.audio_path
        threshold = context.scene.threshold
        print("Normalizing:", audio_path, threshold)
        return {'FINISHED'}
```

This works.

But it assumes:

* Properties live directly on `context.scene`.
* Storage location is fixed.
* UI and logic are tightly coupled.

It cannot be embedded cleanly into another host.

---

## Step 1 – Extract the Core Logic

Separate execution from Blender context:

```python id="fnyq4p"
def normalize_audio(audio_path, threshold):
    print("Normalizing:", audio_path, threshold)
```

Now the function is pure.

It no longer depends on `context`.

The Blender-specific layer becomes a wrapper, not the core.

---

## Step 2 – Declare Shared Keys

Instead of directly accessing scene properties,
declare shared inputs explicitly:

```python id="6o3s6g"
@op(
    label="Normalize Audio",
    space="SEQUENCE_EDITOR",
    category="Audio",
    shared={
        "audio_path": "project.audio_path",
        "threshold": "project.threshold",
    },
)
def normalize_audio(
    audio_path: Path,
    threshold: float = -1.0,
):
    print("Normalizing:", audio_path, threshold)
```

This does three things:

* Removes direct scene coupling.
* Declares the input contract explicitly.
* Makes the tool host-agnostic.

The function now speaks in shared keys, not storage paths.

---

## Step 3 – Generate the Plugin

Run:

```bash id="6dfz3v"
quickaddon build normalize.py
```

You now have:

```text id="1c3g5s"
normalize_plugin/
├── __init__.py
└── generated_ops.py
```

This plugin:

* Declares shared keys.
* Supports fallback storage.
* Can run standalone.
* Can be embedded into any host.

No assumptions about storage are embedded in it.

---

## What Changed?

Before:

* The operator assumed a storage location.
* It could not be embedded cleanly.
* Logic was tied to a specific add-on.

After:

* Logic is pure.
* Inputs are declarative.
* Storage is routed by the host.
* The plugin is reusable.

---

## What Did Not Change?

* The normalization logic.
* The UI label.
* The intended workflow.
* The operator behavior.

Only the structure changed.

---

## The Composability Test

If a tool can:

* Declare shared keys.
* Avoid direct context access.
* Avoid owning storage.

Then it is a proper plugin.

Plugins should not:

* Decide where data lives.
* Perform orchestration.
* Assume execution order.

Those responsibilities belong to the host.

---

## The Architectural Symmetry

Chapter 11:

Existing add-on → Host

Chapter 12:

Existing add-on → Plugin

Together, these chapters define the system boundary.

Hosts own:

* UI composition
* Shared storage
* Orchestration
* Constraint validation

Plugins own:

* Tool logic
* Input declaration
* Stateless execution

That separation is the foundation of composability.

---

## Where You Are Now

You have seen:

* Scripts turned into tools
* Tools turned into plugins
* Plugins embedded into hosts
* Hosts managing routing
* Hosts coordinating execution
* Legacy add-ons refactored in both directions

You now understand the full architectural loop.

The rest is composition.
