---

title: Multi-Plugin Hosts and Generated Routing

---

# {{ page.title }}



At this point, you have built a proper host.

Inside `audiodeck`:

* Shared keys are centralized in `KEYMAP`.
* `HostAPI` routes through that map.
* Fallback storage remains intact.
* Plugins remain unaware of storage details.

The system is clean.
It scales.
It is generic.

You now have a host that can serve any embedded plugin.

---

## Serving Multiple Plugins

Suppose you embed a second plugin `audio_render`:

```text id="1vtnp0"
audiodeck/
├── audio_encode/
└── audio_render/
```

Registration:

```python id="d8p7a1"
audio_encode_ops.register(
    mode="plugin",
    host_api=AudioDeckHostAPI()
)
audio_encode_ops.mount_instance("encode")

audio_render_ops.register(
    mode="plugin",
    host_api=AudioDeckHostAPI()
)
audio_render_ops.mount_instance("render")
```

Both plugins speak in shared keys.

Both are routed through the same `KEYMAP`. Update the `KEYMAP` to include `audio_render's` routing.

Routing is based on keys — not plugin identity.

Your host is now a system boundary.

---

## The Routing Layer Is Generic

Notice what your `HostAPI` does **not** do:

* It does not know which plugin requested a key.
* It does not track plugin identity.
* It does not contain business logic.

Everything flows through:

```text id="x6e2kn"
Plugin → HostAPI → KEYMAP → Storage
```

This is composability.

Plugins snap into the host.
Shared keys connect through the map.
Ownership remains centralized.

---

## Look at What You Built

You wrote:

* A declarative `KEYMAP`
* A mechanical `HostAPI`
* A predictable registration + mounting pattern

There is no dynamic behavior in this routing layer.
No heuristics.
No introspection.

It is entirely structural.

---

## A Natural Question

If this structure is predictable…

If every host follows the same pattern…

If shared keys are already declared in decorators…

Why are we writing this by hand?

Let’s pause on the idea of generated keymap routing.

With this idea:

* Shared keys declared in the host are collected.
* Embedded plugin shared keys are collected.
* A `KEYMAP` is generated.
* A default `HostAPI` is emitted.
* Fallback behavior is preserved.

The structure you just implemented manually could, in principle, be generated automatically.

---

## Build Manually, Then Automate

You now understand:

* The contract
* The ownership model
* The routing boundary

Automation without understanding creates dependency.
Understanding before automation creates control.

That is why we built the routing layer manually first.

We will revisit automation much later in the book.

Before that, we need to cover a few more structural foundations.

---

## Where We Stand

At this stage:

* Hosts own UI.
* Hosts own shared data.
* Multiple plugins are supported.
* Routing is centralized.
* Plugin instances are explicit and named.
* Generation removes boilerplate.

But how does this fit into the existing add-on ecosystem?

In Chapter 11, we will step outside the generated world and refactor a hand-written add-on into a host.

Next, we address an important issue for add-on developers — and how the generator proposes a disciplined solution.
