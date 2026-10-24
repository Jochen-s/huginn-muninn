"""Every surface that states the version must agree with pyproject.toml.

The project drifted to five different version literals (CLI 0.1.0, OpenAPI
0.3.0, api_version 0.16.0, pyproject 0.14.0, README 0.15.0) because each was
edited by hand. One source, one test that reads every surface.
"""
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _pyproject_version() -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["version"]


def test_package_version_matches_pyproject():
    from huginn_muninn import __version__

    assert __version__ == _pyproject_version()


def test_api_envelope_version_matches_pyproject():
    from huginn_muninn.contracts import AnalysisResponse

    assert AnalysisResponse.model_fields["api_version"].default == _pyproject_version()


def test_openapi_version_matches_pyproject():
    from huginn_muninn.api import app

    assert app.version == _pyproject_version()


def test_changelog_latest_release_matches_pyproject():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    first_release = re.search(r"^## \[(\d+\.\d+\.\d+)\]", text, re.MULTILINE)
    assert first_release, "CHANGELOG.md has no released version heading"
    assert first_release.group(1) == _pyproject_version()


def test_readme_footer_matches_pyproject():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    footer = re.search(r"Current version: v(\d+\.\d+\.\d+)", text)
    assert footer, "README.md has no 'Current version' footer"
    assert footer.group(1) == _pyproject_version()
