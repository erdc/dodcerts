import pytest
import re
import sys

from argparse import ArgumentError
from io import StringIO
from unittest import mock

from dodcerts import __version__

help_msg = [
    r'usage: .* \[-h\] \[-V\]\n',
    r'\n',
    r'dodcerts is a tool that provides the DoD Certificate chain as a PEM bundle.\n',
    r'Returns path to file.\n',
    r'\n',
    r'optional arguments:\n',
    r'  -h, --help     Show this help message and exit.\n',
    r'  -V, --version  Show the dodcerts version number and exit\n',
]

ver_msg = ['dodcerts ' + __version__]

@pytest.mark.parametrize('arg, output, regex', [
    (['-h'], help_msg, True),
    (['--help'], help_msg, True),
    (['-V'], ver_msg, False),
    (['--version'], ver_msg, False),
])
def test_parser(arg, output, regex):
    try:
        from dodcerts.cli import parse_args
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
    if regex:
        for l in output:
            assert re.match(l, res.readline()) != None
    else:
        for l in output:
            assert res.readline().find(l) == 0
    # check for end of output
    assert res.readline() == ''
