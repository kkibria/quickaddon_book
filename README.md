# This repo consists of all my quickaddon_book

Read the [quickaddon_book](https://kkibria.github.io/quickaddon_book).

This book can be hosted at github pages.

## Developing content
Make sure rust is up to date.
```
rustup update
```

install mdbook
```
cargo install mdbook
```

install frontmatter processor
```
cargo install --git https://github.com/kkibria/mdbook-frntmtr.git
```

If you have all of the above set up, run.
```
mdbook serve --open
```
will run mdbook server locally and live update with changes. This terminal will be blocked. You can stop the server by pressing control-c.

### adding a new document
Add the new file in `SUMMARY.md` while mdbook server is running.
mdbook will create the file but there will be no frontmatter. How to add frontmatter will be described next. 

## Command like tools
We will use a few Command line tools or CLI for accomplishing a few common tasks. 
These commands are created with python that runs in a virtual environment. We use 
`uv` python package manager to manage the virtual environment. So you will need `uv` installed to proceed. 

You can do them while the mdbook server is running. But you will need to use another terminal window to run these commands from the project directory.  

run, 
```bash
uv sync
```
Will get all the dependencies loaded.


### Activate the virtual environment
macOS / Linux:
```bash
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
.venv\Scripts\activate
```

Windows (Command Prompt):
```cmd
.venv\Scripts\activate.bat
```

The commands will be described next. All these commands must be run from project root folder.

## Deploy to gitub pages
```bash
deploy
```

## Fix frontmatter
```bash
fixfm
```

## Fix Summary
```bash
fixsum
```

## Hydrate book with a list of chapters
You can hydrate from a toml. Look at `revision1.toml` as an example.
This command will crate all the empty chapters with titles provided.
Then you can go and type content in these chapters.

For this example,
```bash
hydrate revision1.toml
```