from pathlib import Path
from importlib.resources import files
from .make_files import get_booksrc
from .fixfm import main as fixfm

def main() -> None:
    booksrc = get_booksrc()
    if booksrc:
        mydir = Path(files(__package__))
        return fixfm(f"./{booksrc}/topics/", mydir / "fm.template")
    else:
        print("book.toml or src in book.toml missing.")