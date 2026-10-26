# @path[tests/conftest.py]
# shared fixtures for the test suite

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

# ==============================================================================
# HELPERS
# ==============================================================================


def _load_module(root: Path, relative: str) -> ModuleType:
    path = root / relative
    name = "".join(char if char.isalnum() else "_" for char in relative.removesuffix(".py"))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load [{path}]")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


# ==============================================================================
# FIXTURES
# ==============================================================================


@pytest.fixture(scope="session")
def repo_root(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath


@pytest.fixture(scope="session")
def load_script(repo_root: Path) -> Callable[[str], ModuleType]:
    cache: dict[str, ModuleType] = {}

    def load(relative: str) -> ModuleType:
        if relative not in cache:
            cache[relative] = _load_module(repo_root, relative)
        return cache[relative]

    return load
