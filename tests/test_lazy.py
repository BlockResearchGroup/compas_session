import pytest

from compas_session.lazyload import LazyLoadSession
from compas_session.lazyload import SingletonError


@pytest.fixture(autouse=True)
def reset_lazy_session():
    LazyLoadSession.delete_instance()
    yield
    LazyLoadSession.delete_instance()


def test_session_noname(tmp_path):
    session = LazyLoadSession(basedir=tmp_path)
    assert session.name == tmp_path.name


def test_session_inheritance(tmp_path):
    class Session(LazyLoadSession):
        pass

    Session.delete_instance()

    session = Session(basedir=tmp_path)
    assert session.name == tmp_path.name

    Session.delete_instance()

    session = Session(name="A", basedir=tmp_path)
    assert session.name == "A"

    session.delete_dirs()


def test_session_name_empty(tmp_path):
    with pytest.raises(SingletonError):
        LazyLoadSession(name="", basedir=tmp_path)


def test_session_singleton(tmp_path):
    a = LazyLoadSession(basedir=tmp_path)
    b = LazyLoadSession(basedir=tmp_path)

    assert a is b

    tests = LazyLoadSession(name=tmp_path.name, basedir=tmp_path)

    assert a is tests

    try:
        LazyLoadSession(name="one", basedir=tmp_path)
    except SingletonError:
        assert True
    else:
        assert False

    a.delete_dirs()
    LazyLoadSession.delete_instance()

    a = LazyLoadSession(name="A", basedir=tmp_path)
    b = LazyLoadSession(basedir=tmp_path)

    assert a is b
    assert a.name == "A"
    assert b.name == "A"
    a.delete_dirs()


def test_session_settings(tmp_path):
    a = LazyLoadSession(basedir=tmp_path)
    b = LazyLoadSession(basedir=tmp_path)

    assert a.settings is b.settings

    a.delete_dirs()


def test_session_settings_values(tmp_path):
    a = LazyLoadSession(basedir=tmp_path)
    b = LazyLoadSession(basedir=tmp_path)

    assert a.settings.autosave is False
    assert b.settings.autosave is False

    a.settings.autosave = True

    assert a.settings.autosave
    assert b.settings.autosave

    a.delete_dirs()
