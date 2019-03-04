from . import _version
__version__ = _version.get_versions()['version']
del _version.get_versions

from .bundle import where
