---

title: Introduction

---

# {{ page.title }}

## QuickAddon

QuickAddon turns plain Python functions into fully working Blender add-ons.

You write the business logic.

QuickAddon generates the Blender-facing structure:

* Operators
* Panels
* Shared-property UI
* A standalone host wrapper
* An embeddable plugin module

No boilerplate.
No Blender ceremony.
No manual class wiring.

We’ll walk through a small example so you get the idea. In **Chapter 3** we will do this for real; for now, treat this as an illustration.

---

## 60-Second Example

Assume you already have a proven Python function. We’ll use a tiny `hello.py`.

File: `hello.py`

```python
def say_hello(name: str):
    print(f"Hello {name}")
```

Now run:

```bash
quickaddon doctor hello.py
```

You’ll see that `quickaddon` has added a small header/preamble at the top of your file.

That preamble is intentional. Among other things, it makes the decorator available as `op` **without you needing to import anything inside your script**.

Now add the decorator to your function:

```python
@op(
    label="Say Hello",
    space="SEQUENCE_EDITOR",
    category="My Tools",
    shared={
        "name": "project.name",
    },
)
def say_hello(name: str):
    print(f"Hello {name}")
```

Then run:

```bash
quickaddon build hello.py --out my_addon_folder
```

The add-on `hello` has been created in `my_addon_folder`.

Install the generated addon in Blender.

Open:

**Video Sequencer → N Panel → My Tools**

You will see:

* A text field for `name`
* A button labeled **Say Hello**

Click it.

You just built a Blender add-on.

No classes.
No register/unregister boilerplate.
No property definitions.
No UI layout code.

Just a function.

> If you’re tempted to try this right now, go ahead.
> But if you want the smoothest learning path, wait until **Chapter 3**—we’ll do this exact workflow there, step by step. For now, treat this as a preview.

---

## What Just Happened?

QuickAddon did three things:

1. Wrapped your function in a Blender Operator.
2. Generated shared properties for `project.name`.
3. Created a standalone host wrapper that injects routing logic.

You didn’t see any of it.

That’s the point.

---

## The Philosophy

Plugins declare what they need.
Hosts decide where data lives.
Shared keys form contracts.

QuickAddon sits in the middle and wires everything together.

You get:

* Clean business logic
* Reusable components
* Embeddable tools
* No fragile path strings
* No copy-paste boilerplate across add-ons

---

## What This Means in Practice

Typical Blender add-ons accumulate:

* Boilerplate
* `PropertyGroup` definitions
* `PointerProperty` wiring
* UI layout code
* Register/unregister juggling

QuickAddon removes that scaffolding from your day-to-day work.

You focus on:

```python
def your_logic(...):
    ...
```

…and let the generator handle the structure.

---

## Next

Now that you’ve seen the shape of it, we’ll explain the mental model.
