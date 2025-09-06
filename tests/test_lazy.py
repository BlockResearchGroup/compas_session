import pytest
from compas_session.lazyload import LazyLoadSession, SingletonError


def test_session_noname():
    LazyLoadSession.delete_instance()

    session = LazyLoadSession()
    assert session.name == "tests"

    session.delete_dirs()


def test_session_inheritance():
    class Session(LazyLoadSession):
        pass

    Session.delete_instance()

    session = Session()
    assert session.name == "tests"

    Session.delete_instance()

    session = Session(name="A")
    assert session.name == "A"

    session.delete_dirs()


@pytest.mark.xfail(raises=SingletonError)
def test_session_name_empty():
    LazyLoadSession.delete_instance()

    session = LazyLoadSession(name="")

    session.delete_dirs()


def test_session_singleton():
    LazyLoadSession.delete_instance()

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
    LazyLoadSession.delete_instance()

    a = LazyLoadSession()
    b = LazyLoadSession()

    assert a.settings is b.settings

    a.delete_dirs()


def test_session_settings_values():
    LazyLoadSession.delete_instance()

    a = LazyLoadSession()
    b = LazyLoadSession()

    assert a.settings.autosave is False
    assert b.settings.autosave is False

    a.settings.autosave = True

    assert a.settings.autosave
    assert b.settings.autosave

    a.delete_dirs()
