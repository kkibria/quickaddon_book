---

title: Mental Model

---

# {{ page.title }}

QuickAddon exists for two kinds of developers:

* Those who want to build Blender tools without writing boilerplate.
* Those whose existing add-ons are growing and need structural separation.

This chapter explains the system in one pass.

If it feels abstract at first, that is intentional.
Each concept becomes concrete in later chapters.

---

## The Problem It Solves

Traditional Blender add-ons tend to mix:

- Tool logic
- UI layout
- Property definitions
- Registration plumbing
- Storage routing

in the same file.

As an add-on grows, this coupling becomes difficult to reason about.

QuickAddon enforces separation between these concerns.

That separation is the foundation of scalability.

---

## Core Separation

QuickAddon separates three concerns:

1. **Tool Logic**
2. **Shared Values**
3. **Storage Ownership**

Understanding these three layers is enough to understand the entire system.

---

## Tool Logic

You write decorated Python functions.

The generator produces:

- Operators
- Panels
- Property definitions
- Registration code

Your source file contains behavior.
The generated code contains structure.

You do not manually define Blender classes.
You do not write `register()` blocks.
You do not manually route properties.

Runtime context (such as `context`, `scene`, etc.) is supplied explicitly through the Injection Contract.

---

## Shared Values

Shared parameters are declared in the decorator:

```python
shared={"audio_path": "project.audio_path"}
````

A shared key:

* Is a stable string identifier
* Is not a Blender property path
* Is an opaque routing key

Multiple tools may reference the same shared key.

The key does not define where data lives.
It defines a contract.

---

## Storage Ownership

A **host** is any add-on that provides storage routing and panel integration for one or more plugins.

In standalone mode, the generated add-on acts as its own host.

In embedded mode, another add-on becomes the host.

Hosts control:

* Where shared values are stored
* How shared UI is drawn
* How plugin instances are scoped

Plugins declare intent.
Hosts enforce routing.

---

## Instance Isolation (Later)

As systems grow, hosts may need multiple independent instances of the same plugin.

That isolation model is introduced later in the book after the v1 routing model is established.

---

## Structural Overview

```
Plugin Function
        ↓
Generated Operator
        ↓
HostAPI (Routing)
        ↓
Host Storage
```

Each layer has one responsibility.

No layer reaches into another layer's storage directly.

---

## Design Constraints

QuickAddon enforces:

* Deterministic host injection
* Centralized shared routing
* Stateless plugin behavior
* No implicit global state

These constraints favor predictability over flexibility.

In large add-on systems, predictability scales better than cleverness.

---

## Summary

You write Python functions.

QuickAddon generates structure.

Hosts control storage and lifecycle.

That is the entire model.
