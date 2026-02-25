import os
import argparse
import sys
from warnings import warn
from .make_files import main as make_files_main

def basedir(kwargs):
    basedir = os.path.expanduser(f"~/.{kwargs['app']}/")
    os.makedirs(basedir, exist_ok=True)
    return basedir

def do_hydrate(toml_file, **kwargs):
    # b = basedir(kwargs)
    make_files_main(toml_file)
    pass

def add_args(parser):
    parser.add_argument('toml_file')
    # parser.add_argument('arg2')
    # parser.add_argument('-f', '--flag', default=False,
                    # action='store_true')

def main():
    params = {"app": "hydrate"}

    parser = argparse.ArgumentParser(
        prog=params["app"],
        description='Creates python command file',
        epilog=f'python -m {params["app"]}')

    add_args(parser)

    args = parser.parse_args()
    params = params | vars(args)

    set_warnigs_hook()
    try:
        do_hydrate(**params)
    except Exception as e:
        print(f'{e.__class__.__name__}:', *e.args)
        return 1
    
    return 0

def set_warnigs_hook():
    import sys
    import warnings
    def on_warn(message, category, filename, lineno, file=None, line=None):
        print(f'Warning: {message}', file=sys.stderr)
    warnings.showwarning = on_warn

if __name__ == '__main__':
    sys.exit(main())
