import importlib.util
import io
import tarfile
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / ".github" / "verify_distributions.py"
SPEC = importlib.util.spec_from_file_location("verify_distributions", SCRIPT)
assert SPEC and SPEC.loader
verify_distributions = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify_distributions)


METADATA = b"""Metadata-Version: 2.4
Name: compas_session
Version: 0.7.0
Requires-Python: >=3.12
Requires-Dist: compas<4,>=3
Requires-Dist: pydantic>=2
"""


def write_wheel(directory, *, typed=True):
    wheel = directory / "compas_session-0.7.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("compas_session/__init__.py", "")
        if typed:
            archive.writestr("compas_session/py.typed", "")
        archive.writestr("compas_session-0.7.0.dist-info/METADATA", METADATA)
    return wheel


def write_sdist(directory):
    sdist = directory / "compas_session-0.7.0.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        for name in ["pyproject.toml", "src/compas_session/py.typed"]:
            info = tarfile.TarInfo(f"compas_session-0.7.0/{name}")
            info.size = 0
            archive.addfile(info, io.BytesIO())
    return sdist


def test_distribution_verification_accepts_complete_artifacts(tmp_path):
    write_wheel(tmp_path)
    write_sdist(tmp_path)
    verify_distributions.verify_distributions(tmp_path)


def test_distribution_verification_rejects_missing_type_marker(tmp_path):
    write_wheel(tmp_path, typed=False)
    write_sdist(tmp_path)
    with pytest.raises(ValueError, match="py.typed"):
        verify_distributions.verify_distributions(tmp_path)


def test_distribution_verification_requires_exact_artifact_set(tmp_path):
    write_wheel(tmp_path)
    with pytest.raises(ValueError, match="exactly one wheel"):
        verify_distributions.verify_distributions(tmp_path)
