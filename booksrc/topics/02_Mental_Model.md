---

title: Mental Model

---

# {{ page.title }}


QuickAddon serves two audiences:

* People who want to build Blender tools without learning the full add-on internals.
* Developers whose existing add-ons are growing and need clearer structural separation.

You can read this book sequentially.
If you already write add-ons, you may skip strategically (see below).

---

## Reading Guide

### If you are new to Blender add-ons

Continue to **Chapter 3**.
You will build a working tool immediately and see the workflow in action.

### If you already write add-ons

You may skim:

* Chapter 3 (basic tool generation)
* Chapter 4 (standalone behavior)

Then jump to:

* Chapter 5 – Embedding Plugins
* Chapter 8 – Property Ownership
* Chapter 11 – Refactoring an Add-on into a Host
* Chapter 12 – Refactoring an Add-on into a Plugin

Those chapters focus on structure, migration, and scaling.

---

## Core Model (Concise Version)

QuickAddon separates three concerns:

1. Tool logic
2. Shared values
3. Storage ownership

Keeping these separate is the key to how the system scales.

---

### Tool Logic

You write decorated Python functions.

The generator produces:

* Operators
* Panels
* Properties
* Registration code

You do not manually define Blender classes or registration blocks.
Your file contains behavior; the generated code contains structure.

---

### Shared Values

Shared parameters are declared in the decorator:

```python
shared={"audio_path": "project.audio_path"}
```

A shared key:

* Is a stable string identifier
* Is **not** a Blender property path
* Is treated as an opaque routing key

Multiple tools may reference the same shared key.

The key itself does not define where data lives.
It only defines a contract.

---

### Storage Ownership

By default:

* Shared values are stored in `Scene.qa_shared`.
* The generated add-on manages this automatically.

When a tool is embedded into a host:

* The host may route shared keys into its own storage.
* The tool code does not change.

This routing is handled through the HostAPI contract.

The plugin declares what it needs.
The host decides where it is stored.

---

## Design Constraints (v1)

QuickAddon v1 intentionally enforces:

* Deterministic host injection
* Single active mapping per plugin module
* Read-only shared access by default
* Explicit write channels only if implemented by the host

These constraints favor predictability over flexibility.

They are not limitations.
They are guardrails.

---

That is the entire mental model.

You write Python functions.
QuickAddon generates structure.
Hosts control storage routing.

If the terms above feel abstract, that’s fine.
Each concept will be unpacked in context in the following chapters.
