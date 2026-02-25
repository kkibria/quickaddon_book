# scan.py checks for title inconsistencies
# between SUMMARY.md and a topic md file
# and fixes it. 

# pip install python-frontmatter
import os
import frontmatter
import regex as re
import pathlib
from .rep_tit import replace_titles
from .make_files import get_booksrc


ignore = ["doclist.md", "SUMMARY.md"]
pattern = re.compile(r'\[([^][]+)\](\(((?:[^()]+|(?2))+)\))')


def normalize(fpn):
    p = pathlib.Path(fpn)
    return str(pathlib.PurePosixPath(p))


def make_doclist():
    doclist = {}
    for top, dirs, files in os.walk("."):
        for fn in files:
            if fn.endswith(".md"):
                fn = normalize(os.path.join(top, fn))
                if fn in ignore:
                    continue
                doclist[fn] = fn
    return doclist


def get_titles(doclist):
    for doc in doclist:
        with open(doc, "r", encoding="utf8") as f:
            meta = frontmatter.load(f)
            if 'title' in meta:
                doclist[doc] = meta['title']
            else:
                doclist[doc] = doc


def make_sumlist():
    sumlist = {}
    with open("SUMMARY.md", "r") as f:
        lines = f.readlines()

    for line in lines:
        m = pattern.search(line)
        if m:
            description, _, url = m.groups()
            doc = normalize(url)
            sumlist[doc] = description
    return sumlist, lines


def report(doclist, sumlist):
    with open("doclist.md", "w") as f:
        for doc in doclist:
            print("[{}]({})".format(doclist[doc], doc), file=f)
            if doc not in sumlist:
                print(f"Missing {doc} in SUMMARY.md")
            else:
                if doclist[doc] != sumlist[doc]:
                    print(f"Title mismatch for {doc} in SUMMARY.md")

def main():
    os.chdir(get_booksrc())
    doclist = make_doclist()
    get_titles(doclist)
    sumlist, lines = make_sumlist()
    report(doclist, sumlist)
    replace_titles("\n".join(lines), doclist)
    print("# SUMMARY.md has been updated with list of current titles.")

if __name__ == "__main__":
    main()