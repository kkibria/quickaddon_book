---

title: Refactoring an Existing Add-on into a Host

---

# {{ page.title }}



So far, we have stayed inside the generated ecosystem.

Now we step outside it.

Suppose you already have a working Blender add-on.

It was written manually.
It grew over time.
It works.
But it feels heavier than it should.

We will refactor it into a proper host.

---

## The Starting Point

Consider a simplified existing add-on:

```python id="0sxy9r"
class AUDIO_OT_encode(bpy.types.Operator):
    bl_idname = "audio.encode"
    bl_label = "Encode Audio"

    def execute(self, context):
        path = context.scene.audio_path
        bitrate = context.scene.bitrate
        print("Encoding:", path, bitrate)
        return {'FINISHED'}


class AUDIO_OT_render(bpy.types.Operator):
    bl_idname = "audio.render"
    bl_label = "Render Audio"

    def execute(self, context):
        path = context.scene.audio_path
        print("Rendering:", path)
        return {'FINISHED'}


class AUDIO_PT_panel(bpy.types.Panel):
    bl_label = "Audio Tools"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Audio"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "audio_path")
        layout.prop(context.scene, "bitrate")
        layout.operator("audio.encode")
        layout.operator("audio.render")
```

This works.

But notice:

* Shared data is accessed directly from `context.scene`.
* Operators assume a specific storage location.
* Logic and UI are tightly coupled.
* Extending this structure requires repetition.

There is no clear ownership boundary.

---

## Step 1 – Separate Ownership

First, formalize storage ownership.

Define a property group:

```python id="ukq8ng"
class AudioHostProps(bpy.types.PropertyGroup):
    audio_path: bpy.props.StringProperty(subtype="FILE_PATH")
    bitrate: bpy.props.IntProperty(default=192)
```

Register it:

```python id="odqahb"
bpy.types.Scene.audio_host = bpy.props.PointerProperty(
    type=AudioHostProps
)
```

Now storage is explicit.

Instead of scattering values across `context.scene`, we centralize them.

---

## Step 2 – Extract Tool Logic

Instead of embedding logic directly inside operators, extract the functional core:

```python id="x8qazn"
def encode_audio(audio_path, bitrate):
    print("Encoding:", audio_path, bitrate)


def render_audio(audio_path):
    print("Rendering:", audio_path)
```

Now logic is reusable and independent of Blender.

Operators become thin wrappers.

---

## Step 3 – Convert Tools into Plugins

Now these functions can become QuickAddon plugins.

They declare shared keys:

```python id="ckd9l5"
@op(
    shared={
        "audio_path": "project.audio_path",
        "bitrate": "project.bitrate",
    }
)
def encode_audio(audio_path: Path, bitrate: int):
    ...
```

And:

```python id="l1znf2"
@op(
    shared={
        "audio_path": "project.audio_path",
    }
)
def render_audio(audio_path: Path):
    ...
```

Generate them as plugins.

These plugins:

* Do not know where storage lives.
* Do not assume `context.scene`.
* Declare only their shared contracts.

---

## Step 4 – Turn the Existing Add-on into a Host

Your original add-on becomes:

* UI owner
* Property owner
* Orchestrator

It embeds the generated plugins.

It defines:

* `KEYMAP`
* `HostAPI`
* Optional orchestration logic

The structure becomes:

```text id="wev0xa"
audio_host/
├── __init__.py
├── encode_plugin/
└── render_plugin/
```

The host controls routing.

The plugins remain modular.

---

## What Changed?

Before:

* Operators directly accessed scene properties.
* Storage was implicit.
* Logic and UI were tightly coupled.

After:

* Host owns storage.
* Plugins declare shared keys.
* Routing is centralized.
* Logic is modular.
* The system becomes composable.

---

## What Did Not Change?

* The core encode logic.
* The core render logic.
* The UI intent.
* The user workflow.

We changed structure, not behavior.

---

## The Result

Your existing add-on:

* Becomes cleaner.
* Gains composability.
* Gains embeddable plugins.
* Gains routing discipline.
* Gains orchestration capability.

And it did not require rewriting everything from scratch.

In the next chapter, we go the other direction:

Refactoring an existing add-on into a reusable plugin.
