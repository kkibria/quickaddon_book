---

title: Cooperative Long-Running Tasks

---

# {{ page.title }}


Now that we have built an add-on and executed our functions, we must address an important concern for serious add-on development.

Up to this point, every plugin function executes immediately.

That works for:

* Small tasks
* Quick transformations
* Lightweight operations

But real tools often perform:

* Frame-by-frame processing
* Batch encoding
* File iteration
* Heavy analysis

If executed in a single operator call, Blender freezes.

Operators run on the main thread.

If a task takes 10 minutes,
the UI blocks for 10 minutes.

That is not acceptable for serious tools.

---

## The Cooperative Model

Instead of blocking execution, we introduce:

> Cooperative long-running tasks.

The idea is simple:

* A task performs a small unit of work.
* It yields control back to Blender.
* The host schedules the next step.
* Progress is tracked.
* The user can cancel.

This is similar to how rendering progresses frame by frame.

Blender stays responsive.

---

## Declaring a Long Task

A plugin may declare:

```python
@op(
    label="Process Frames",
    long_task=True,
)
def process_frames(...):
    ...
```

If `long_task=True`, the function must follow a contract.

That contract defines:

* How incremental work is performed
* How progress is reported
* How cancellation is respected
* How cleanup is handled

Plugins do not implement scheduling.

The host owns execution control.

---

## Cancellation Model

Cancellation must be explicit and predictable.

QuickAddon long tasks must provide a visible cancellation mechanism
similar to Blender's "Render Animation" operator.

The host must provide:

- A progress indicator
- A visible cancel control (e.g., button or "X")
- Proper cleanup on cancellation

ESC behavior:

ESC may cancel the task **only when the long-task modal operator
actively owns execution focus**, similar to Blender rendering.

ESC must not:

- Cancel unrelated background work
- Interfere with normal Blender interaction
- Trigger cancellation unintentionally while the user performs other actions

The recommended model mirrors Blender’s native rendering workflow:

User starts task  
→ Progress appears  
→ Cancel button is visible  
→ ESC cancels only while task is modal-owner  

Cancellation is a host responsibility.
Plugins must tolerate interruption.

---

## Why This Matters

As tools grow:

* Processing time increases
* Users expect responsiveness
* Cancellation becomes critical
* Stability becomes non-negotiable

A disciplined long-task model allows:

* Non-blocking execution
* Progress feedback
* Safe cancellation
* Predictable lifecycle management

We will define the full long-task contract and implementation details in Chapter 13.

For now, understand the boundary:

Plugins may declare long tasks.
Hosts own scheduling and execution control.

In the next chapter, we step outside the generated ecosystem and refactor an existing add-on into a host.
