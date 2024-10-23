import datetime
import os
import pathlib
import tempfile
from typing import Any
from typing import Callable
from typing import Optional
from typing import Union

import compas
import compas.data
import compas.datastructures
import compas.geometry
import compas.tolerance
from compas.scene import Scene


class NamedSessionError(Exception):
    pass


class NamedSession:
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

    """

    _instances = {}
    _is_inited = False

    def __new__(cls, *, name: str, **kwargs):
        if name not in cls._instances:
            instance = object.__new__(cls)
            instance._is_inited = False
            cls._instances[name] = instance
        return cls._instances[name]

    def __init__(
        self,
        name: Optional[str] = None,
        basedir: Optional[Union[str, pathlib.Path]] = None,
    ) -> None:
        if not self._is_inited:
            self.name = name
            self.data = {}
            self.current = -1
            self.depth = 53
            self.history = []
            self.timestamp = int(datetime.datetime.timestamp(datetime.datetime.now()))
            self.basedir = basedir
        self._is_inited = True

    @property
    def tempdir(self):
        if self.basedir:
            tempdir = pathlib.Path(self.basedir) / "temp"
            tempdir.mkdir(exist_ok=True)

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
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

        """
        if key not in self.data:
            return default
        return self.data[key]

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

    def load(self, filepath: Union[str, pathlib.Path]) -> None:
        """Replace the session data with the data of a session stored in a file.

        Parameters
        ----------
        filepath : str | Path
            Location of the file containing the session data.

        Returns
        -------
        None

        """
        self.reset()
        self.data = compas.json_load(filepath)

    def dump(self, filepath: Union[str, pathlib.Path]) -> None:
        """Dump the data of the current session into a file.

        Parameters
        ----------
        filepath : str | Path
            Location of the file containing the session data.

        Returns
        -------
        None

        """
        compas.json_dump(self.data, filepath)

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

        self.current -= 1
        filepath, _ = self.history[self.current]
        self.data = compas.json_load(filepath)

        return True

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
        if self.current == len(self.history) - 1:
            print("Nothing more to redo!")
            return False

        self.current += 1
        filepath, _ = self.history[self.current]
        self.data = compas.json_load(filepath)

        return True

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

        fd, filepath = tempfile.mkstemp(dir=self.tempdir, suffix=".json", text=True)

        compas.json_dump(self.data, filepath)
        self.history.append((filepath, name))

        h = len(self.history)
        if h > self.depth:
            self.history[:] = self.history[h - self.depth :]
        self.current = len(self.history) - 1

    def reset(self) -> None:
        """Reset session history.

        Returns
        -------
        None

        """
        self.current = -1
        self.depth = 53
        for filepath, eventname in self.history:
            try:
                os.unlink(filepath)
            except PermissionError:
                pass
            except Exception:
                pass
        self.history = []

    # =============================================================================
    # Firs-class citizens
    # =============================================================================

    def scene(self, name: Optional[str] = None) -> Scene:
        """Return the scene with the given name if it is in the session.
        Otherwise create a new scene in the session under the given name and return it.

        Parameters
        ----------
        name : str, optional
            The name of the scene.
            If none is provided, the following name is used ``f"{self.name}.Scene"``.

        Returns
        -------
        :class:`Scene`

        """
        name = name or f"{self.name}.Scene"
        scene: Scene = self.setdefault(name, factory=Scene)
        scene.name = name
        return scene
