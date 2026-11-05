import datetime
import os
import pathlib
import shutil
import sys
from collections.abc import Callable
from typing import Any
from typing import ClassVar
from typing import Self

import compas
from compas.geometry import Brep
from compas.scene import Scene
from compas.tolerance import TOL

from .settings import Settings


class SingletonError(Exception):
    """Raised when the active singleton is requested with another name."""

    pass


class LazyLoadSessionError(Exception):
    """Base exception for lazy-load session errors."""

    pass


# Sessiondir
# - tolerance.json
# - version(s).json
# - states
# -- <state identifier>
# --- scene.json
# --- settings.json
# --- data
# ---- <key>.json
# ---- <key>.json
# ---- <key>.json
# ---- <key>.json
#
# Recording a state
# 1. dump current state to active record
# 2. copy active record to record with different name
# 3. add record name to history
# 4. remove all records forward from active (no more redo possible, only undo)
#
# Undo
# 1. dump current state to active record
# 2. set active record to current - 1, if possible
# 3. clear data dict
# 4. load scene (link scene object items to matching data items based on guid)
#
# Redo
# 1. dump current state to active record
# 2. set active record to current + 1, if possible
# 3. clear data dict
# 4. load scene (link scene object items to matching data items based on guid)


class LazyLoadSession:
    """Class representing a data session that can be identified by its name.

    A lazy-load session stores data in separate files below its session
    directory. Only one instance exists per class during the lifetime of a
    process.

    Raises
    ------
    SingletonError
        If the active singleton is requested with a different name.

    """

    @classmethod
    def delete_instance(cls) -> None:
        """Forget the active singleton instance without deleting its files."""

        cls._instance = None

    _instance: ClassVar[Any | None] = None

    _name: str
    _timestamp: int
    _basedir: pathlib.Path
    _history: list[tuple[str, str]]
    _current: int
    _depth: int = 53
    _data: dict[str, Any]
    _settings: Settings
    _scene: Scene

    # this can be overwritten in a child class
    # to influence the default settings and scene objects
    settingsclass: ClassVar[type[Settings]] = Settings
    sceneclass: ClassVar[type[Scene]] = Scene

    def __new__(
        cls,
        *,
        name: str | None = None,
        basedir: str | os.PathLike[str] | None = None,
        scene: Scene | None = None,
        settings: Settings | None = None,
        depth: int | None = None,
        delete_existing: bool = False,
    ) -> Self:
        if cls._instance is None:
            if basedir:
                basedir = pathlib.Path(basedir)
            else:
                # basedir = pathlib.Path(sys.argv[0]).resolve().parent
                # basedir = pathlib.Path().cwd()
                basedir = pathlib.Path(sys._getframe(1).f_globals["__file__"]).parent

            if not name:
                for filepath in basedir.iterdir():
                    if filepath.is_dir():
                        if filepath.suffix == ".session":
                            name = filepath.stem
                            break

            if not name:
                name = basedir.parts[-1]

            instance = object.__new__(cls)

            instance._name = name
            instance._timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
            instance._basedir = basedir
            instance._current = -1
            instance._depth = depth or cls._depth
            instance._history = []
            instance._data = {}
            instance._settings = settings or instance.settingsclass()
            instance._scene = scene or instance.sceneclass()

            if delete_existing:
                instance.delete_dirs()
            instance.create_dirs()

            instance.load_tolerance()

            cls._instance = instance

        return cls._instance

    def __init__(self, **kwargs: Any) -> None:
        # this is accessed when the singleton is accessed in Rhino during consecutive command calls
        # or for example during a live session on a server
        if "name" in kwargs:
            name = kwargs["name"]
            if name != self.name:
                raise SingletonError
        self.load_history()

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Data: {self.data}",
                f"Tolerance: {TOL}",
                f"Settings: {self.settings}",
                f"Scene: {self.scene}",
                f"History: {self.history}",
            ]
        )

    @property
    def name(self) -> str:
        """str: Name of the session."""

        return self._name

    @property
    def timestamp(self) -> int:
        """int: Unix timestamp captured when the session was created."""

        return self._timestamp

    @property
    def basedir(self) -> pathlib.Path:
        """pathlib.Path: Working directory containing the session directory."""

        return self._basedir

    @property
    def sessiondir(self) -> pathlib.Path:
        """pathlib.Path: Root directory of this session."""

        return self.basedir / f"{self.name}.session"

    @property
    def datadirname(self) -> str:
        """str: Name of the data directory."""

        return "data"

    @property
    def datadir(self) -> pathlib.Path:
        """pathlib.Path: Directory containing separately stored data values."""

        return self.sessiondir / self.datadirname

    @property
    def recordsdirname(self) -> str:
        """str: Name of the history-record directory."""

        return "__records"

    @property
    def recordsdir(self) -> pathlib.Path:
        """pathlib.Path: Directory containing history records."""

        return self.sessiondir / self.recordsdirname

    @property
    def tempdirname(self) -> str:
        """str: Name of the session temporary directory."""

        return "__temp"

    @property
    def tempdir(self) -> pathlib.Path:
        """pathlib.Path: Session temporary directory."""

        return self.sessiondir / self.tempdirname

    @property
    def historyfilename(self) -> str:
        """str: Filename of the history metadata."""

        return "_history.json"

    @property
    def historyfile(self) -> pathlib.Path:
        """pathlib.Path: Path of the history metadata."""

        return self.sessiondir / self.historyfilename

    @property
    def scenefilename(self) -> str:
        """str: Filename of the serialized scene."""

        return "_scene.json"

    @property
    def scenefile(self) -> pathlib.Path:
        """pathlib.Path: Path of the serialized scene."""

        return self.sessiondir / self.scenefilename

    @property
    def settingsfilename(self) -> str:
        """str: Filename of the serialized settings."""

        return "_settings.json"

    @property
    def settingsfile(self) -> pathlib.Path:
        """pathlib.Path: Path of the serialized settings."""

        return self.sessiondir / self.settingsfilename

    @property
    def tolerancefilename(self) -> str:
        """str: Filename of the serialized COMPAS tolerance."""

        return "_tolerance.json"

    @property
    def tolerancefile(self) -> pathlib.Path:
        """pathlib.Path: Path of the serialized COMPAS tolerance."""

        return self.sessiondir / self.tolerancefilename

    @property
    def versionfilename(self) -> str:
        """str: Filename of the serialized COMPAS version."""

        return "_version.json"

    @property
    def versionfile(self) -> pathlib.Path:
        """pathlib.Path: Path of the serialized COMPAS version."""

        return self.sessiondir / self.versionfilename

    @property
    def current(self) -> int:
        """int: Index of the active history record."""

        return self._current

    @property
    def depth(self) -> int:
        """int: Maximum number of history records retained."""

        return self._depth

    @property
    def history(self) -> list[tuple[str, str]]:
        """list[tuple[str, str]]: Record identifiers and their names."""

        return self._history

    @property
    def scene(self) -> Scene:
        """compas.scene.Scene: Scene stored by the session."""

        if not self._scene:
            if self.scenefile.exists():
                scene = compas.json_load(self.scenefile)
                if isinstance(scene, self.sceneclass):
                    self._scene = scene
        return self._scene

    @scene.setter
    def scene(self, value: Scene) -> None:
        if not isinstance(value, self.sceneclass):
            raise ValueError
        self._scene = value

    @property
    def settings(self) -> Settings:
        """Settings: Settings stored by the session."""

        if not self._settings:
            if self.settingsfile.exists():
                self._settings = self.settingsclass(**compas.json_load(self.settingsfile))
        return self._settings

    @settings.setter
    def settings(self, value: Settings) -> None:
        if not isinstance(value, self.settingsclass):
            raise ValueError
        self._settings = value

    @property
    def data(self) -> dict[str, Any]:
        """dict[str, Any]: Values currently loaded in memory."""

        return self._data

    @data.setter
    def data(self, value: dict[str, Any]) -> None:
        if not isinstance(value, self.__class__.__annotations__["_data"].__origin__):
            raise ValueError
        self._data = value

    # =============================================================================
    # Dict behaviour
    # =============================================================================

    def __contains__(self, key: Any) -> bool:
        value = self.get(key)
        if value is None and key not in self.data:
            return False
        return True

    def __getitem__(self, key: str) -> Any:
        value = self.get(key)
        if value is None and key not in self.data:
            raise KeyError
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value)

    # =============================================================================
    # Directory management
    # =============================================================================

    def delete_dirs(self) -> None:
        """Remove all directories."""
        shutil.rmtree(self.datadir, ignore_errors=True)
        shutil.rmtree(self.recordsdir, ignore_errors=True)
        shutil.rmtree(self.tempdir, ignore_errors=True)
        shutil.rmtree(self.sessiondir, ignore_errors=True)

    def create_dirs(self) -> None:
        """Create all directories."""
        self.sessiondir.mkdir(exist_ok=True, parents=True)
        self.tempdir.mkdir(exist_ok=True, parents=True)
        self.recordsdir.mkdir(exist_ok=True, parents=True)
        self.datadir.mkdir(exist_ok=True, parents=True)

    # =============================================================================
    # Tolerance
    # =============================================================================

    def load_tolerance(self) -> None:
        """Load the tolerance from the corresponding session file, if it exists."""
        if self.tolerancefile.exists():
            compas.json_load(self.tolerancefile)

    def dump_tolerance(self) -> None:
        """Dump the current tolerance setting to the corresponding session file."""
        compas.json_dump(TOL, self.tolerancefile)

    # =============================================================================
    # Settings
    # =============================================================================

    def load_settings(self) -> None:
        """Load the settings from the corresponding session file, if it exists."""
        if self.settingsfile.exists():
            self.settings = compas.json_load(self.settingsfile)

    def dump_settings(self) -> None:
        """Dump the current settings to the corresponding session file."""
        compas.json_dump(self.settings, self.settingsfile)

    # =============================================================================
    # Scene
    # =============================================================================

    def load_scene(self) -> None:
        """Load the scene from the corresponding session file, if it exists."""
        if self.scenefile.exists():
            self.scene = compas.json_load(self.scenefile)

    def dump_scene(self) -> None:
        """Dump the current scene to the corresponding session file."""
        compas.json_dump(self.scene, self.scenefile)

    # =============================================================================
    # Data
    # =============================================================================

    def get(
        self,
        key: str,
        default: Any = None,
        filepath: str | os.PathLike[str] | None = None,
    ) -> Any:
        """Return the value for `key` if `key` is in the session, else return `default` or None.

        Parameters
        ----------
        key
            The identifier of the data value.
        default
            A default value.

        Returns
        -------
        Any
            The session data value corresponding to the key/identifier,
            or the default value if no entry with the given key/identifier exists.

        filepath
            Optional explicit source file. JSON and STEP files are supported.

        """
        if key not in self.data:
            filepath = pathlib.Path(filepath or self.datadir / f"{key}.json")

            if filepath.exists():
                if filepath.suffix == ".obj":
                    raise NotImplementedError
                elif filepath.suffix == ".stp":
                    value = Brep.from_step(str(filepath))
                elif filepath.suffix == ".json":
                    value = compas.json_load(str(filepath))
                else:
                    raise NotImplementedError

                self.data[key] = value
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Insert `key` in the session, and assign `value` to it.

        Parameters
        ----------
        key
            The session key.
        value
            The value assigned to `key` in the session.

        """
        self.data[key] = value
        if self.settings.autosync:
            compas.json_dump(value, self.datadir / f"{key}.json")

    def setdefault(self, key: str, factory: Callable[[], Any]) -> Any:
        """Return the value of `key` in the session.
        If `key` doesn't exist in the session, assign and return the result of calling `factory`.

        Parameters
        ----------
        key
            The session key.
        factory
            A callable factory object to generate a value if `key` is missing.

        Returns
        -------
        Any

        """
        if key not in self.data:
            self.set(key, factory())
        return self.get(key)

    def delete(self, key: str) -> None:
        """Delete a data item from storage.

        Parameters
        ----------
        key
            The name of the item.

        """
        if key in self.data:
            del self.data[key]

        filepath = self.datadir / f"{key}.json"
        if filepath.exists():
            filepath.unlink()

        filepath = self.datadir / f"{key}.obj"
        if filepath.exists():
            filepath.unlink()

        filepath = self.datadir / f"{key}.stp"
        if filepath.exists():
            filepath.unlink()

    # =============================================================================
    # Complete state
    # =============================================================================

    def dump(self, sessiondir: str | os.PathLike[str] | None = None) -> None:
        """Dump the data of the current session into the session directory.

        Parameters
        ----------
        sessiondir
            Reserved destination directory. The current implementation writes
            to this session's configured directory.

        """
        if not sessiondir:
            if not self.sessiondir:
                raise ValueError("No base directory is set and no filepath is provided.")
            sessiondir = self.sessiondir
        sessiondir = pathlib.Path(sessiondir)

        self.dump_history()
        # self.dump_scene()
        # self.dump_settings()
        # self.dump_tolerance()
        # self.dump_version()
        # self.dump_data()

        compas.json_dump(self.scene, self.scenefile)
        compas.json_dump(self.settings.model_dump(), self.settingsfile)
        compas.json_dump(TOL, self.tolerancefile)
        compas.json_dump(compas.__version__, self.versionfile)

        for key in self.data:
            value = self.data[key]

            if isinstance(value, Brep):
                filepath = self.datadir / f"{key}.stp"
                value.to_step(filepath)
            else:
                filepath = self.datadir / f"{key}.json"
                compas.json_dump(value, filepath)

    # =============================================================================
    # History
    # =============================================================================

    def load_history(self) -> None:
        """Load the session history."""
        if self.historyfile.exists():
            history = compas.json_load(self.historyfile)
            self._depth = history["depth"]
            self._current = history["current"]
            self._history = history["records"]

    def dump_history(self) -> None:
        """Dump the session history."""
        history = {"depth": self.depth, "current": self.current, "records": self.history}
        compas.json_dump(history, self.historyfile)

    def clear_history(self) -> None:
        """Clear session history."""
        self._current = -1
        self._depth = self.__class__._depth
        for record, _ in self.history:
            folder = self.recordsdir / record
            shutil.rmtree(folder, ignore_errors=True)
        self._history = []

    def record(self, name: str) -> None:
        """Record the current state of the session into session history.

        Parameters
        ----------
        name
            The name of the recording.

        """
        if self.current > -1:
            if self.current < len(self.history) - 1:
                self.history[:] = self.history[: self.current + 1]

        record = f"{datetime.datetime.timestamp(datetime.datetime.now())}"
        folder = self.recordsdir / record
        folder.mkdir()
        self.history.append((record, name))
        self.dump()

        shutil.copytree(self.datadir, folder / self.datadirname)
        shutil.copy(self.scenefile, folder / self.scenefilename)
        shutil.copy(self.settingsfile, folder / self.settingsfilename)
        shutil.copy(self.tolerancefile, folder / self.tolerancefilename)
        shutil.copy(self.versionfile, folder / self.versionfilename)

        h = len(self.history)
        if h > self.depth:
            self.history[:] = self.history[h - self.depth :]
        self._current = len(self.history) - 1

    def undo(self) -> bool:
        """Move one step backward in recorded session history.

        Returns
        -------
        bool
            True if the state was successfully changed.
            False otherwise.

        Notes
        -----
        If there are no remaining backward steps in recorded history,
        nothing is done and the function returns False.

        """
        if self.current < 0:
            print("Nothing to undo!")
            return False

        if self.current == 0:
            print("Nothing more to undo!")
            return False

        self._current -= 1
        record, name = self.history[self.current]
        folder = self.recordsdir / record

        print(f"Loading: {name}")

        if folder.exists() and folder.is_dir():
            shutil.rmtree(self.datadir)
            self.scenefile.unlink()
            self.settingsfile.unlink()
            self.tolerancefile.unlink()
            self.versionfile.unlink()

            shutil.copytree(folder / self.datadirname, self.datadir)
            shutil.copy(folder / self.scenefilename, self.scenefile)
            shutil.copy(folder / self.settingsfilename, self.settingsfile)
            shutil.copy(folder / self.tolerancefilename, self.tolerancefile)
            shutil.copy(folder / self.versionfilename, self.versionfile)

            self.dump_history()
            return True

        return False

    def redo(self) -> bool:
        """Move one step forward in recorded session history.

        Returns
        -------
        bool
            True if the state was successfully changed.
            False otherwise.

        Notes
        -----
        If there are no remaining forward steps in recorded history,
        nothing is done and the function returns False.

        """
        if self.current >= len(self.history) - 1:
            print("Nothing more to redo!")
            return False

        self._current += 1
        record, name = self.history[self.current]
        folder = self.recordsdir / record

        print(f"Loading: {name} ({record})")

        if folder.exists() and folder.is_dir():
            shutil.rmtree(self.datadir)
            self.scenefile.unlink()
            self.settingsfile.unlink()
            self.tolerancefile.unlink()
            self.versionfile.unlink()

            shutil.copytree(folder / self.datadirname, self.datadir)
            shutil.copy(folder / self.scenefilename, self.scenefile)
            shutil.copy(folder / self.settingsfilename, self.settingsfile)
            shutil.copy(folder / self.tolerancefilename, self.tolerancefile)
            shutil.copy(folder / self.versionfilename, self.versionfile)

            self.dump_history()
            return True

        return False

    # =============================================================================
    # Versioning
    # =============================================================================

    # pull
    # push
    # sync
    # merge
    # diff
