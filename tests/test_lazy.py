import pytest

from compas_session.lazyload import LazyLoadSession, LazyLoadSessionError


def test_session_noname():
    with pytest.raises(TypeError):
        LazyLoadSession()


def test_session_name_empty():
    with pytest.raises(LazyLoadSessionError):
        LazyLoadSession(name=None)
    with pytest.raises(LazyLoadSessionError):
        LazyLoadSession(name="")


def test_session_singleton():
    session1a = LazyLoadSession(name="One")
    session1b = LazyLoadSession(name="One")
    session2a = LazyLoadSession(name="Two")
    session2b = LazyLoadSession(name="Two")

    assert session1a is session1b
    assert session2a is session2b

    assert session1a is not session2a
    assert session1a is not session2b
    assert session1b is not session2a
    assert session1b is not session2b


def test_session_settings():
    session1a = LazyLoadSession(name="One")
    session1b = LazyLoadSession(name="One")
    session2a = LazyLoadSession(name="Two")
    session2b = LazyLoadSession(name="Two")

    assert session1a.settings is session1b.settings
    assert session2a.settings is session2b.settings

    assert session1a.settings is not session2a.settings
    assert session1a.settings is not session2b.settings
    assert session1b.settings is not session2a.settings
    assert session1b.settings is not session2b.settings


def test_session_settings_values():
    session1 = LazyLoadSession(name="One")
    session2 = LazyLoadSession(name="Two")

    assert session1.settings.autosave is False
    assert session2.settings.autosave is False

    session1.settings.autosave = True

    assert session1.settings.autosave
    assert not session2.settings.autosave
