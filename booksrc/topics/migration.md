---
title: v1 to v2 Migration
---


# {{ page.title }}

QuickAddon does not provide a runtime compatibility layer between tracks.
Migration is regeneration-based.

## Core Rule

- `v1` and `v2` are parallel tracks.
- To move to `v2`, regenerate with `--track v2`.

## Migration Steps

1. Keep your tool source functions and `@op` declarations.
2. Ensure filename stem follows canonical policy: `^[a-z_][a-z0-9_]*$`.
3. Rebuild with v2:

```bash
quickaddon build my_tool.py --out "$BLENDER_ADDON" --track v2 --force
```

4. Host integration uses scoped API:
- register plugin in plugin mode with unbound host API
- add explicit instances with `add_instance(instance_hint="...")`

## What Changes Operationally

- Shared resolution becomes scoped (`scope + key`).
- Host controls scope lifecycle and routing.
- Multiple instances of the same plugin become first-class.

## What Stays Stable

- Tool function source logic.
- Shared key declarations.
- Injection contract model (`inject={...}`).
- Long-task contract (`long_task=True` generator semantics).

## Common Migration Errors

- Invalid source filename stem:
  - `QA10-FILENAME-INVALID`
- Attempting `--name` override:
  - `QA10-FILENAME-OVERRIDE-DISALLOWED`
- Shared key type mismatch across ops:
  - `QA10-SHARED-KEY-TYPEMISMATCH`

