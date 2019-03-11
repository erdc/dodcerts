import pytest
import sys

from argparse import ArgumentError
from io import StringIO
from unittest import mock

from dodcerts.dodcerts import __version__

help_msg = [
    'usage: pytest [-h] [-V]\n',
    '\n',
    'dodcerts is a tool that provides the DoD Certificate chain as a PEM bundle.\n',
    'Returns path to file.\n',
    '\n',
    'optional arguments:\n',
    '  -h, --help     Show this help message and exit.\n',
    '  -V, --version  Show the dodcerts version number and exit\n',
]

ver_msg = ['dodcerts ' + __version__]

unrec_msg = [
    'usage: pytest [-h] [-V]\n',
    'pytest: error: unrecognized arguments: bad_input\n',
]

@pytest.mark.parametrize('arg, output', [
    (['-h'], help_msg),
    (['--help'], help_msg),
    (['-V'], ver_msg),
    (['--version'], ver_msg),
])
def test_parser(arg, output):
    try:
        from dodcerts.dodcerts.cli import parse_args
    except:
        assert False

    with mock.patch('sys.stdout', new_callable=StringIO):
        try:
            p = parse_args(arg)
        except SystemExit:
            # avoid exit
            pass
        res = StringIO(sys.stdout.getvalue())

    # compare output
    for l in output:
        str = res.readline()
        assert str == l
        #assert res.readline().find(l) == 0
    # check for end of output
    assert res.readline() == ''
