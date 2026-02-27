from pathlib import Path
import tomllib
from toolslib.safe_write import safe_open_write

text1="""
1. Introduction — The Copy-Paste Reward
2. The Mental Model — Why Addons Rot
3. First Plugin — Declarative, Not Imperative
4. Standalone Host — How Execution Is Owned
5. Embedding Plugins — Composition Without Coupling
6. Shared Keys — Stable Contracts
7. HostAPI v1 — Deterministic Routing
8. Property Ownership — Who Really Owns Data
9. Why V1 Exists — Choosing the Right Track
10. HostAPI v2 — Scoped Composition
11. Multi-Plugin Systems — Nested Hosts
12. Storage Model — IDProperties and KEYMAP
13. Long Task Contract — Strict by Design
14. Scheduler Preview — Host-Controlled Execution
15. Diagnostics — QA10 and QA20
16. Refactoring an Existing Addon into a Plugin
17. Refactoring an Existing Addon into a Host
18. Migration Strategy — Regenerate, Don't Patch
19. Why QuickAddon Is Strict
20. Architectural Guarantees
"""
def safe_name(name) -> str:
    name = "".join(ch if ((ch.isalnum() or ch in "_-") and ch not in "$'\"~") else "_" for ch in name)
    return name
          
def make_files(destpath, text, stripcnt):
    doc = Path(destpath)
    doc.mkdir(parents=True, exist_ok=True)
    sumpath = doc.parent / f"SUMMARY.md"

    with safe_open_write(sumpath) as sf:    
        for i, line in enumerate(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            a = line.split()
            if a[0] == "#":
                # its a group heading
                title = " ".join(a[1:])
                print(f"\n# {title.title()}", file=sf)
                continue

            title = " ".join(a[stripcnt:])
            mdname = "_".join(title.split())
            mdname = safe_name(mdname)
            mdname = f"{i:02}_{mdname}.md"
            md = doc / mdname
            tag = "{{ page.title }}"
            x = f"""---

title: {title}

---

# {tag}

"""

            with md.open("w") as f:
                print(x, file=f)

            print(f"- [{title}]({doc.stem}/{mdname})", file=sf)
            print(f"Created {md}")

def read_toml(file_path):
    try:
        with open(file_path, "rb") as f:
            data = tomllib.load(f)
            return data
        
        # You can now access the data like a normal Python dictionary
        # print(f"Title: {data.get('title')}")
        # print(f"Enabled: {data.get('data')['enabled']}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except tomllib.TOMLDecodeError as e:
        print(f"Error decoding TOML file: {e}")

def get_booksrc():
    bk = Path("./book.toml")
    if bk.exists:
        bkdata = read_toml(bk)
        try:
            return bkdata["book"]["src"]
        except:
            pass

def main(toml_file):
    toml = Path(toml_file)
    # look for book.tml file in the current directory
    src = get_booksrc()
    if src:
        data = read_toml(toml)
        strip = data.get("strip", 0)
        # print(data["sections"])
        make_files(f"{src}/{toml.stem}", data["docs"], strip)
    else:
        print("Cant find book.toml or src in current directory.")