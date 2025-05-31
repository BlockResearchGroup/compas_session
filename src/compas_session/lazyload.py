import datetime
import os
import pathlib
import shutil
from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

import compas
from compas.geometry import Brep
from compas.scene import Scene
from compas.tolerance import Tolerance

from .settings import Settings

# NOTES
# -----
# a session should not be loaded explicitly
# to load a session
# just unset all stored data
# this will trigger lazy re-loading of the data from the (new) system files and data dir


class LazyLoadSessionError(Exception):
    pass


class LazyLoadSession:
    """Class representing a data session that can be identified by its name.

    The class is implemented such that each named instance is a singleton.
    This means that during the lifetime of a program only one instance with a specific can exist,
    and that all sessions created with the same name, refer to the same session object instance.

    Parameters
    ----------
    name : str
        The name of the unique object instance.
    basedir : str or Path-like, optional
        A "working" directory that serves as the root
        for storing (temporary) session data.

    Raises
    ------
    SessionError
        If no name is provided.

    """

    _instances = {}

    _name: str
    _timestamp: int
    _basedir: pathlib.Path
    _history: list[tuple[str, str]]
    _current: int
    _depth: int = 53
    _data: dict[str, Any]
    _settings: Settings
    _scene: Scene
    _tolerance: Tolerance

    # this can be overwritten in a child class
    # to influence the default settings and scene objects
    settingsclass = Settings
    sceneclass = Scene

    def __new__(
        cls,
        *,
        name: str,
        basedir: Optional[Union[str, pathlib.Path]] = None,
        scene: Optional[Scene] = None,
        settings: Optional[Settings] = None,
        tolerance: Optional[Tolerance] = None,
        depth: Optional[int] = None,
        delete_existing: bool = False,
    ):
        if not name:
            # this can be used to force initialisation in a Rhino session
            # by not providing a name in "non-init commands"
            # for example all but one
            raise LazyLoadSessionError("A session name is required.")

        if name not in cls._instances:
            # this is accessed at the beginning of every workflow script
            # or the first time the session is created in a Rhino command session
            # or in a live server session
            # or on the cli
            # all possible data
            instance = object.__new__(cls)
            cls._instances[name] = instance

            instance._name = name
            instance._timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
            instance._basedir = pathlib.Path(basedir or os.getcwd())
            instance._current = -1
            instance._depth = depth or cls._depth
            instance._history = []
            instance._data = {}
            instance._tolerance = tolerance or instance.load_tolerance() or Tolerance()
            instance._settings = settings or instance.settingsclass()
            instance._scene = scene or instance.sceneclass()

            if delete_existing:
                instance.delete_dirs()
            instance.create_dirs()

        return cls._instances[name]

    def __init__(self, **kwargs) -> None:
        # this is accessed when the singleton is accessed in Rhino during consecutive command calls
        # or for example during a live session on a server
        pass

    def __str__(self) -> str:
        return "\n".join(
            [
                f"Data: {self.data}",
                f"Tolerance: {self.tolerance}",
                f"Settings: {self.settings}",
                f"Scene: {None}",
                f"History: {self.history}",
            ]
        )

    @property
    def name(self):
        return self._name

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def basedir(self):
        return self._basedir

    @property
    def sessiondir(self) -> pathlib.Path:
        return self.basedir / f"{self.name}.session"

    @property
    def datadir(self) -> pathlib.Path:
        return self.sessiondir / "__data"

    @property
    def recordsdir(self) -> pathlib.Path:
        return self.sessiondir / "__records"

    @property
    def tempdir(self) -> pathlib.Path:
        return self.sessiondir / "__temp"

    @property
    def historyfile(self) -> pathlib.Path:
        return self.sessiondir / "__history.json"

    @property
    def scenefile(self) -> pathlib.Path:
        return self.sessiondir / "__scene.json"

    @property
    def settingsfile(self) -> pathlib.Path:
        return self.sessiondir / "__settings.json"

    @property
    def tolerancefile(self) -> pathlib.Path:
        return self.sessiondir / "__tolerance.json"

    @property
    def current(self):
        return self._current

    @property
    def depth(self):
        return self._depth

    @property
    def history(self):
        return self._history

    @property
    def scene(self):
        if not self._scene:
            if self.scenefile.exists():
                scene = compas.json_load(self.scenefile)
                if isinstance(scene, self.sceneclass):
                    self._scene = scene
        return self._scene

    @scene.setter
    def scene(self, value):
        if not isinstance(value, self.sceneclass):
            raise ValueError
        self._scene = value

    @property
    def settings(self):
        if not self._settings:
            if self.settingsfile.exists():
                self._settings = self.settingsclass(**compas.json_load(self.settingsfile))
        return self._settings

    @settings.setter
    def settings(self, value):
        if not isinstance(value, self.settingsclass):
            raise ValueError
        self._settings = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if not isinstance(value, self.__class__.__annotations__["_data"].__origin__):
            raise ValueError
        self._data = value

    @property
    def tolerance(self) -> Tolerance:
        return self._tolerance

    @tolerance.setter
    def tolerance(self, tolerance: Tolerance) -> None:
        self._tolerance.update_from_dict(tolerance.__data__)
        compas.json_dump(self._tolerance, self.tolerancefile)

    # =============================================================================
    # Dict behaviour
    # =============================================================================

    def __contains__(self, key) -> bool:
        value = self.get(key)
        if value is None and key not in self.data:
            return False
        return True

    def __getitem__(self, key) -> Any:
        value = self.get(key)
        if value is None and key not in self.data:
            raise KeyError
        return value

    def __setitem__(self, key, value) -> None:
        self.set(key, value)

    # =============================================================================
    # Directory management
    # =============================================================================

    def delete_dirs(self) -> None:
        """Remove all directories.

        Returns
        -------
        None

        """
        shutil.rmtree(self.datadir, ignore_errors=True)
        shutil.rmtree(self.recordsdir, ignore_errors=True)
        shutil.rmtree(self.tempdir, ignore_errors=True)
        shutil.rmtree(self.sessiondir, ignore_errors=True)

    def create_dirs(self) -> None:
        """Create all directories.

        Returns
        -------
        None

        """
        self.sessiondir.mkdir(exist_ok=True)
        self.tempdir.mkdir(exist_ok=True)
        self.recordsdir.mkdir(exist_ok=True)
        self.datadir.mkdir(exist_ok=True)

    # =============================================================================
    # Tolerance
    # =============================================================================

    def load_tolerance(self) -> Optional[Tolerance]:
        if self.tolerancefile.exists():
            tolerance = compas.json_load(self.tolerancefile)
            if isinstance(tolerance, Tolerance):
                return tolerance

    # =============================================================================
    # Data
    # =============================================================================

    def get(self, key: str, default: Any = None, filepath: Optional[pathlib.Path] = None) -> Any:
        """Return the value for `key` if `key` is in the session, else return `default` or None.

        Parameters
        ----------
        key : str
            The identifier of the data value.
        default : Any, optional
            A default value.

        Returns
        -------
        Any
            The session data value corresponding to the key/identifier,
            or the default value if no entry with the given key/identifier exists.

        Raises
        ------
        KeyError
            If the value with the requested key is not available in the session and no default is given.

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
        key : str
            The session key.
        value : Any
            The value assigned to `key` in the session.

        Returns
        -------
        None

        """
        self.data[key] = value
        if self.settings.autosync:
            compas.json_dump(value, self.datadir / f"{key}.json")

    def setdefault(self, key: str, factory: Callable) -> Any:
        """Return the value of `key` in the session.
        If `key` doesn't exist in the session, assign and return the result of calling `factory`.

        Parameters
        ----------
        key : str
            The session key.
        factory : Callable
            A callable factory object to generate a valu if `key` is missing.

        Returns
        -------
        Any

        """
        if key not in self.data:
            self.set(key, factory())
        return self.get(key)

    # =============================================================================
    # State
    # =============================================================================

    def dump(self, sessiondir: Optional[Union[str, pathlib.Path]] = None) -> None:
        """Dump the data of the current session into a session directory.

        Parameters
        ----------
        sessiondir : str | Path
            Location of the file containing the session data.

        Returns
        -------
        None

        """
        if not sessiondir:
            if not self.sessiondir:
                raise ValueError("No base directory is set and no filepath is provided.")
            sessiondir = self.sessiondir
        sessiondir = pathlib.Path(sessiondir)

        history = {"depth": self.depth, "current": self.current, "records": self.history}

        compas.json_dump(history, self.historyfile)
        compas.json_dump(self.scene, self.scenefile)
        compas.json_dump(self.settings.model_dump(), self.settingsfile)
        compas.json_dump(self.tolerance, self.tolerancefile)

        for key in self.data:
            value = self.data[key]

            if isinstance(value, Brep):
                filepath = self.datadir / f"{key}.stp"
                value.to_step(filepath)
            else:
                filepath = self.datadir / f"{key}.json"
                compas.json_dump(value, filepath)

    def load(self, sessiondir: Optional[Union[str, pathlib.Path]] = None, clear_history: bool = True) -> None:
        """Replace the session data with the data of a session directory.

        Parameters
        ----------
        sessiondir : str | Path, optional
            Location of the folder containing the session data files.
        clear_history : bool, optional
            Clear the current history before loading the new data.

        Returns
        -------
        None

        """
        if not sessiondir:
            if not self.sessiondir:
                raise ValueError("No base directory is set and no filepath is provided.")
            sessiondir = self.sessiondir

        # if clear_history:
        #     self.clear_history()

        if self.historyfile.exists():
            history = compas.json_load(self.historyfile)
            self._depth = history["depth"]
            self._current = history["current"]
            self._history = history["records"]

        if self.scenefile.exists():
            self.scene = compas.json_load(self.scenefile)

        if self.settingsfile.exists():
            self.settings = self.settingsclass(**compas.json_load(self.settingsfile))

        if self.datadir.exists():
            for filepath in self.datadir.iterdir():
                name = filepath.stem

                if filepath.suffix == ".obj":
                    raise NotImplementedError
                elif filepath.suffix == ".stp":
                    value = Brep.from_step(filepath)
                elif filepath.suffix == ".json":
                    value = compas.json_load(filepath)
                else:
                    raise NotImplementedError

                self.data[name] = value

    # =============================================================================
    # History
    # =============================================================================

    def clear_history(self) -> None:
        """Clear session history.

        Returns
        -------
        None

        """
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
        name : str
            The name of the current state.

        Returns
        -------
        None

        """
        if self.current > -1:
            if self.current < len(self.history) - 1:
                self.history[:] = self.history[: self.current + 1]

        record = f"{datetime.datetime.timestamp(datetime.datetime.now())}"
        folder = self.recordsdir / record
        folder.mkdir()
        self.history.append((record, name))
        self.dump()

        shutil.copytree(self.datadir, folder / "__data")
        shutil.copy(self.scenefile, folder / "__scene.json")
        shutil.copy(self.settingsfile, folder / "__settings.json")

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
        record, _ = self.history[self.current]
        folder = self.recordsdir / record

        if folder.exists() and folder.is_dir():
            shutil.rmtree(self.datadir)
            shutil.copytree(folder / "__data", self.datadir)

            self.scenefile.unlink()
            shutil.copy(folder / "__scene.json", self.scenefile)

            self.settingsfile.unlink()
            shutil.copy(folder / "__settings.json", self.settingsfile)

            self.load()
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
        raise NotImplementedError
        # if self.current == len(self.history) - 1:
        #     print("Nothing more to redo!")
        #     return False

        # self._current += 1
        # filepath, _ = self.history[self.current]

        # self.load(filepath, reset=False)
        # return True
