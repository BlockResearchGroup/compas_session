import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

from packaging.requirements import Requirement


def find_distributions(directory: Path) -> tuple[Path, Path]:
    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Expected exactly one wheel and one source distribution.")
    if not wheels[0].stat().st_size or not sdists[0].stat().st_size:
        raise ValueError("Distribution files must not be empty.")
    return wheels[0], sdists[0]


def verify_wheel(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if "compas_session/py.typed" not in names:
            raise ValueError("Wheel does not contain compas_session/py.typed.")
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            raise ValueError("Wheel must contain exactly one METADATA file.")
        metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))

    if metadata["Requires-Python"] != ">=3.12":
        raise ValueError("Wheel has an unexpected Requires-Python value.")

    requirements = {requirement.name: requirement for value in metadata.get_all("Requires-Dist", []) for requirement in [Requirement(value)]}
    compas = requirements.get("compas")
    pydantic = requirements.get("pydantic")
    if not compas or str(compas.specifier) != "<4,>=3":
        raise ValueError("Wheel has an unexpected COMPAS dependency.")
    if not pydantic or str(pydantic.specifier) != ">=2":
        raise ValueError("Wheel has an unexpected Pydantic dependency.")


def verify_sdist(sdist: Path) -> None:
    with tarfile.open(sdist) as archive:
        names = archive.getnames()
    roots = {name.split("/", 1)[0] for name in names}
    if len(roots) != 1:
        raise ValueError("Source distribution must have one root directory.")
    root = roots.pop()
    required = {f"{root}/pyproject.toml", f"{root}/src/compas_session/py.typed"}
    if not required.issubset(names):
        raise ValueError("Source distribution is missing project metadata or py.typed.")


def verify_distributions(directory: Path) -> None:
    wheel, sdist = find_distributions(directory)
    verify_wheel(wheel)
    verify_sdist(sdist)


if __name__ == "__main__":
    verify_distributions(Path(sys.argv[1]))
