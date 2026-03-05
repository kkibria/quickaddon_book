---

title: QA Scaffold CLI Reference

---

# {{ page.title }}

`qa-scaffold` is a convention-first CLI for generating and operating QuickAddon QA scaffold projects.

The workflow is Python-only and designed to hide shell orchestration behind stable subcommands.

## Command Surface

```bash
qa-scaffold init <path>
qa-scaffold build [--config <path>]
qa-scaffold sync [--config <path>]
```

## Standard Flow

1. Initialize scaffold:

```bash
qa-scaffold init ./qa_scaffolding
```

2. Enter scaffold project and hydrate:

```bash
cd qa_scaffolding
uv sync
```

3. Build generated addon:

```bash
uv run qa-scaffold build
```

4. Build and copy to sync target:

```bash
uv run qa-scaffold sync
```

## Config Contract

Default config file in scaffold root:

```text
qa_scaffold.toml
```

Typical defaults:

```toml
plugin_script = "src/sample_plugin.py"
out_dir = "build/addons"
sync_dir = "build/synced"
track = "v2"
force = true
doctor = true
blender = "4.0"
```

Rules:

- Config paths are resolved relative to the config file location.
- `track` must be `v1` or `v2`.
- `sync` runs `build` first, then copies output to `sync_dir`.

## Convention Policy

- Users should not run shell scripts directly for scaffold operations.
- Canonical execution path is `uv run qa-scaffold <subcommand>`.
- Plugin identity still follows QuickAddon filename-stem policy.

## Output Layout

After build/sync, expected structure is:

```text
<scaffold>/build/addons/<plugin_stem>/...
<scaffold>/build/synced/<plugin_stem>/...
```
