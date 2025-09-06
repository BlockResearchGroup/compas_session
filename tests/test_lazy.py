import pytest
from compas_session.lazyload import LazyLoadSession, SingletonError


def test_session_noname():
    LazyLoadSession.reset()

    session = LazyLoadSession()
    assert session.name == "tests"

    session.delete_dirs()


def test_session_inheritance():
    class Session(LazyLoadSession):
        pass

    Session.reset()

    session = Session()
    assert session.name == "tests"

    Session.reset()

    session = Session(name="A")
    assert session.name == "A"

    session.delete_dirs()


@pytest.mark.xfail(raises=SingletonError)
def test_session_name_empty():
    LazyLoadSession.reset()

    session = LazyLoadSession(name="")

    session.delete_dirs()


def test_session_singleton():
    LazyLoadSession.reset()

    a = LazyLoadSession()
    b = LazyLoadSession()

    assert a is b

    tests = LazyLoadSession(name="tests")

    assert a is tests

    try:
        LazyLoadSession(name="one")
    except SingletonError:
        assert True
    else:
        assert False

    a.delete_dirs()


def test_session_settings():
    LazyLoadSession.reset()

    a = LazyLoadSession()
    b = LazyLoadSession()

    assert a.settings is b.settings

    a.delete_dirs()


def test_session_settings_values():
    LazyLoadSession.reset()

    a = LazyLoadSession()
    b = LazyLoadSession()

    assert a.settings.autosave is False
    assert b.settings.autosave is False

    a.settings.autosave = True

    assert a.settings.autosave
    assert b.settings.autosave

    a.delete_dirs()
