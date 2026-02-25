---

title: Diagnostics and Contract Enforcement

---

# {{ page.title }}



QuickAddon enforces architectural contracts.

Strictness is intentional.

When a rule is violated, the system does not guess.
It fails early and clearly.

Each diagnostic includes:

* A stable error code
* File and function location (when applicable)
* A concise explanation
* A direct fix suggestion

Error codes follow this format:

```text id="1r2bka"
QA<layer>-<area>-<rule>
```

Where:

* `QA10` → Build-time validation
* `QA20` → Runtime enforcement
* `area` → `LONGTASK`, `SHARED`, `HOSTAPI`, etc.

---

## Build-Time Validation

Build-time errors prevent invalid add-ons from being generated.

These diagnostics enforce structural correctness before Blender ever loads the add-on.

They are the most critical safeguards.

---

### QA10-LONGTASK-NOTGEN

Triggered when:

* `long_task=True` is declared
* The function contains no `yield` or `yield from`

Example:

```text id="4vkl4b"
[QA10-LONGTASK-NOTGEN] my_tool.py:42 in process_frames
long_task=True requires a generator function (use 'yield' or 'yield from').
```

Fix:

* Add incremental `yield` steps
* Or remove `long_task=True`

---

### QA10-LONGTASK-ASYNC

Triggered when:

* `async def` is used with `long_task=True`

Async generators are not supported.

Fix:

* Use a standard generator (`def`, not `async def`)

---

### QA10-SHARED-KEY-TYPEMISMATCH

Triggered when:

* The same shared key is declared with incompatible types across functions

Fix:

* Ensure consistent type usage for the shared key

Shared keys must have stable type semantics across the system.

---

## Runtime Contract Enforcement

Runtime errors occur inside Blender during execution.

They indicate a contract violation that passed build validation but failed during execution.

---

### QA20-LONGTASK-RETURNED-NONGEN

Triggered when:

* A `long_task=True` function returns a non-generator object at runtime

Example:

```text id="pcv50e"
[QA20-LONGTASK-RETURNED-NONGEN] process_frames
long_task function did not return a generator.
```

Fix:

* Ensure the function contains `yield`
* Ensure execution does not return early before yielding

---

### QA20-LONGTASK-YIELD-NONDICT

Triggered when:

* The generator yields something other than a dictionary

Fix:

* Yield a dictionary containing `progress` and `total`

---

### QA20-LONGTASK-YIELD-MISSING-FIELDS

Triggered when:

* The yield payload omits required fields

Minimum required fields:

```text id="v9ttqf"
progress
total
```

Optional:

```text id="awq6d2"
message
```

Fix:

* Include required fields in every yield

The host relies on these fields for scheduling and progress reporting.

---

### QA20-LONGTASK-EXCEPTION

Triggered when:

* The generator raises an exception

Behavior:

* Execution stops
* Progress UI closes
* The error is reported through Blender’s operator report system

Fix:

* Correct the underlying exception

Unhandled exceptions terminate the task immediately.

---

## Design Philosophy

QuickAddon diagnostics are:

* Deterministic
* Searchable
* Stable across versions

Strictness is not punishment.

It guarantees:

* Non-blocking execution
* Predictable routing
* Isolation between instances
* Stable nested composition

Architectural contracts are enforced so systems remain reliable at scale.
