import itertools
import json
import subprocess
from pathlib import Path

import pytest
from _pytest.fixtures import FixtureRequest
from pytest_django.fixtures import SettingsWrapper


def is_e2e(request: FixtureRequest) -> bool:
    """Check if the current test is marked as an end-to-end (e2e) test.

    See:
        https://docs.pytest.org/en/stable/reference/reference.html#request
    """
    return bool(list(request.node.iter_markers_with_node(name="e2e")))


def _webpack_path(settings: SettingsWrapper, static_file: str) -> Path:
    return Path(f"{settings.STATIC_ROOT}/webpack_bundles/{static_file}")


def all_webpack_files_exist(settings: SettingsWrapper) -> bool:
    """Check to see if all webpack files exist in STATIC_ROOT."""
    stats = json.loads((Path(settings.BASE_DIR) / "webpack-stats.json").read_text())
    static_files = itertools.chain.from_iterable(stats.get("chunks", {}).values())
    return all(_webpack_path(settings, static_file).exists() for static_file in static_files)


@pytest.fixture(autouse=True)
def conditional_webpack(request: FixtureRequest, settings: SettingsWrapper):
    """For e2e tests, remove the test configuration of the webpack loader class to use the real webpack assets.

    See:
        https://docs.pytest.org/en/stable/reference/reference.html#request
        https://pytest-django.readthedocs.io/en/latest/helpers.html#settings
        https://django-webpack-loader.readthedocs.io/en/latest/#loader_class
    """
    if is_e2e(request):
        if not all_webpack_files_exist(settings):
            subprocess.run(["make", "collectstatic"], check=True, cwd=settings.BASE_DIR)  # noqa: S607

        if "DEFAULT" in settings.WEBPACK_LOADER and "LOADER_CLASS" in settings.WEBPACK_LOADER["DEFAULT"]:
            # This should always be set from the test settings, but wasn't in at CI test run
            del settings.WEBPACK_LOADER["DEFAULT"]["LOADER_CLASS"]
