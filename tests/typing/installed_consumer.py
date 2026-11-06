from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from typing import assert_type

from compas.scene import Scene
from compas_session.lazyload import LazyLoadSession
from compas_session.session import Session
from compas_session.settings import Settings

with TemporaryDirectory() as directory:
    basedir = Path(directory)
    settings = Settings(autosave=False, autosync=True)
    scene = Scene()

    session = Session(name="typed-session", basedir=basedir, scene=scene, settings=settings)
    session.set("iteration", 1)
    assert_type(settings, Settings)
    assert_type(scene, Scene)
    assert_type(session, Session)
    assert_type(session.get("iteration"), Any)
    assert_type(session.dump(basedir / "typed-session.json"), None)

    lazy = LazyLoadSession(name="typed-lazy-session", basedir=basedir, scene=scene, settings=settings)
    lazy.set("iteration", 1)
    assert_type(lazy, LazyLoadSession)
    assert_type(lazy.get("iteration"), Any)
    assert_type(lazy.dump(basedir / "typed-lazy-session.session"), None)
