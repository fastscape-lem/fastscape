from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("fastscape")
except PackageNotFoundError:  # noqa
    # package is not installed
    pass

from fastscape import processes
from fastscape import models

__all__ = ["processes", "models"]
