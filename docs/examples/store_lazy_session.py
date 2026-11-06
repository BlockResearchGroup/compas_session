from tempfile import TemporaryDirectory

from compas_session.lazyload import LazyLoadSession

with TemporaryDirectory() as directory:
    session = LazyLoadSession(name="design", basedir=directory)
    session["iteration"] = 1
    assert session["iteration"] == 1

    session.record("first iteration")
    session.delete_dirs()
    LazyLoadSession.delete_instance()
