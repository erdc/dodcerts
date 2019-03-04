import sys

import argparse
from argparse import _HelpAction

from . import __version__

def parse_args(args):
    '''Parse command line arguments
    
    Args:
        args(iterable):
            passed to argparser 

    Returns:
        argparser parsing results
    '''
    p = argparse.ArgumentParser(
        description='dodcerts is a tool that provides the DoD Certificate chain as a PEM bundle. Returns path to file.',
        add_help=False,
    )
    p.add_argument(
        '-h', '--help',
        action=_HelpAction,
        help="Show this help message and exit.",
    )
    p.add_argument(
        '-V', '--version',
        action='version',
        version='dodcerts %s' % __version__,
        help="Show the dodcerts version number and exit",
    )
    return p.parse_args(args)

def cli():
    '''Command line interface for package

    Returns:
        the filepath of the DoD Certificate chain as a PEM bundle
    '''
    parse_args(sys.argv[1:])
    print(str(dodcerts.where()))
