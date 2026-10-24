"""Huginn & Muninn -- fact-checking with common humanity."""
from importlib.metadata import PackageNotFoundError, version as _pkg_version

try:
    # Single source of truth: the version in pyproject.toml, via the
    # installed package metadata. tests/test_version_sync.py checks every
    # surface that states it.
    __version__ = _pkg_version("huginn-muninn")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0.0.0+unknown"
