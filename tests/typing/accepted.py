from pathlib import Path
from typing import assert_type

from compas_session.lazyload import LazyLoadSession
from compas_session.session import Session
from compas_session.settings import Settings


settings = Settings(autosave=True)
session = Session(name="example", basedir=Path("."), settings=settings)
lazy = LazyLoadSession(name="example", basedir=Path("."), settings=settings)

assert_type(session, Session)
assert_type(lazy, LazyLoadSession)
assert_type(session.settings, Settings)
assert_type(lazy.settings, Settings)
