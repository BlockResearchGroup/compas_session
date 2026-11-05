# Tutorial

## Store one complete session

[`Session`][compas_session.session.Session] returns the same object whenever it
is constructed with the same name. Use a base directory when you want the
default dump path to be predictable.

```python
from tempfile import TemporaryDirectory

from compas_session.session import Session

with TemporaryDirectory() as directory:
    session = Session(name="design", basedir=directory)
    session["iteration"] = 1
    session.dump()

    assert Session(name="design") is session
    assert session["iteration"] == 1
```

Calling `record(name)` writes a temporary snapshot. `undo()` and `redo()` move
through the recorded snapshots when another state is available.

## Store values in separate files

[`LazyLoadSession`][compas_session.lazyload.LazyLoadSession] creates a
`<name>.session` directory. With the default settings, assigning a value writes
it immediately to the session's `data` directory because `autosync` is enabled.

```python
from tempfile import TemporaryDirectory

from compas_session.lazyload import LazyLoadSession

with TemporaryDirectory() as directory:
    session = LazyLoadSession(name="design", basedir=directory)
    session["iteration"] = 1
    assert session["iteration"] == 1

    session.record("first iteration")
    session.delete_dirs()
    LazyLoadSession.delete_instance()
```

Call `delete_instance()` when an application intentionally ends the singleton's
lifetime. Call `delete_dirs()` only when its persisted files should also be
removed.

## Configure synchronization

Pass a [`Settings`][compas_session.settings.Settings] object to choose whether
clients should autosave and whether lazy-load assignments should be synchronized
to disk.

```python
from compas_session.settings import Settings

settings = Settings(autosave=False, autosync=True)
```
