---

title: First Plugin

---

## {{ page.title }}



Since you are intending to write an add-on, it is useful to know where Blender expects add-ons to live.

Open Blender.

Go to the **Scripting** workspace and locate the **Python Console**.

Type:

```python
>>> import addon_utils
>>> addon_utils.paths()
[
    '/Applications/Blender-454.app/Contents/Resources/4.5/scripts/addons_core',
    '/Users/user/Library/Application Support/Blender/4.5/scripts/addons'
]
```

On my system, user-installed add-ons live in:

```
/Users/user/Library/Application Support/Blender/4.5/scripts/addons
```

Your path may differ depending on OS and Blender version.

It is helpful to store this location in an environment variable so you don’t have to type it repeatedly.

Add it to your shell configuration file (for example, `~/.zshrc` or `~/.bashrc`).
In this book, we will assume the variable is named:

```
BLENDER_ADDON
```

From now on, we will use `$BLENDER_ADDON` whenever we refer to your add-on directory.

---

## From Script Editor to Button

Assume this is your starting point:

You wrote a function.
You pasted it into Blender’s Script Editor.
You ran it.
It works.

Example:

```python
from pathlib import Path

def setup_from_audio(
    audio_path: Path,
    bpm: int = 120,
):
    print("Audio:", audio_path)
    print("BPM:", bpm)
```

You tested it manually.
Now you want a button inside Blender that runs it.

You do not want to learn add-on boilerplate.

---

### Step 1 – Save It to a File

Save the script as:

```
audiodeck.py
```

---

### Step 2 – Insert the Required Header

Run:

```bash
quickaddon doctor audiodeck.py
```

This inserts the canonical header block.

Do not edit the header.

Your file now contains something like:

```python
# QUICKADDON_HEADER_BEGIN <hash>
...
# QUICKADDON_HEADER_END <hash>

from pathlib import Path

def setup_from_audio(
    audio_path: Path,
    bpm: int = 120,
):
    print("Audio:", audio_path)
    print("BPM:", bpm)
```

The header enables QuickAddon to process your file correctly. It must remain intact.

---

### Step 3 – Add the `@op` Decorator

Add metadata above your function:

```python
@op(
    label="Setup From Audio",
    space="SEQUENCE_EDITOR",
    category="QuickAddon",
)
def setup_from_audio(
    audio_path: Path,
    bpm: int = 120,
):
    print("Audio:", audio_path)
    print("BPM:", bpm)
```

That is the only structural change.

You did not convert it into a class.
You did not define a Blender Operator manually.
You did not import `bpy`.

---

### Step 4 – Build the Add-on

Now build it into the Blender add-on directory we identified earlier:

```bash
quickaddon build audiodeck.py \
  --out $BLENDER_ADDON \
  --force
```

Open Blender.

Go to **Edit → Preferences → Add-ons**.

Search for **Setup From Audio** and enable it.

From now on, Blender will load this add-on automatically.

Open:

**SEQUENCE_EDITOR → N-panel → QuickAddon**

You now have:

* A button labeled **Setup From Audio**
* A popup dialog for `audio_path` and `bpm`

Click **Run**.

Your original function executes.

That’s it.

---

### Step 5 – Add More Functions

Let’s add a second function to the same file.

```python
@op(
    label="Setup From Audio",
    space="SEQUENCE_EDITOR",
    category="QuickAddon",
)
def setup_from_audio(
    audio_path: Path,
    bpm: int = 120,
):
    print("Setup:", audio_path, bpm)


@op(
    label="Render From Audio",
    space="SEQUENCE_EDITOR",
    category="QuickAddon",
)
def render_from_audio(
    audio_path: Path,
):
    print("Render:", audio_path)
```

Rebuild and re-enable.

What you will see:

* Two buttons
* Two popup dialogs
* Each function asks for `audio_path` independently

That is perfectly valid if the two audio paths should be separate.

But if both tools are meant to operate on the same audio file, repeatedly entering the path becomes unnecessary.

This is where shared values come in.

---

### Now Make It Shared

Modify both decorators:

```python
@op(
    label="Setup From Audio",
    space="SEQUENCE_EDITOR",
    category="QuickAddon",
    shared={
        "audio_path": "project.audio_path",
    },
)
def setup_from_audio(
    audio_path: Path,
    bpm: int = 120,
):
    print("Setup:", audio_path, bpm)


@op(
    label="Render From Audio",
    space="SEQUENCE_EDITOR",
    category="QuickAddon",
    shared={
        "audio_path": "project.audio_path",
    },
)
def render_from_audio(
    audio_path: Path,
):
    print("Render:", audio_path)
```

Rebuild.

Now you will see:

* `audio_path` appears once in the panel.
* It no longer appears in popup dialogs.
* Both functions use the same stored value.
* The value persists across runs.

You enter the path once.

Both functions use it.

That is what “shared” means.

You did not write storage code.
You only declared that both functions reference the same shared key.

Persistence is handled for you.

---

If this feels clean and predictable, that is intentional.

In the next chapter, we will examine how the generated host makes this possible.
