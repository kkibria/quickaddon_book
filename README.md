# This repo consists of all my programming recipes

Read the [cookbook](https://kkibria.github.io/my_cookbook).

Read this [page](https://kkibria.github.io/my_cookbook/topics/text-content.html)
to understand how to do initial setup for deployment after you clone this repo.

## Developing content
make sure rust is up to date
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
will run mdbook server locally and live update with changes.

### adding a new document
Add the new file in `SUMMARY.md` while mdbook server is running.
mdbook will create the file. Now go edit the file to add the frontmatter and title.


## deploying setup 
This is one time setup after cloning the repo. 
Copy `setup.ps1_` to `temp.ps1` and run `temp.ps1`. It might give
an error message, 'fatal: couldn't find remote ref gh-pages'. Not to worry. Delete `temp.ps1`.

## deploy
run `deploy.ps1`


## fix frontmatter
from project root type,
```
fixfm
```
