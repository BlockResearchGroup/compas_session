import pytest

from compas_session.session import Session, SessionError


def test_session_noname():
    with pytest.raises(TypeError):
        Session()


def test_session_name_empty():
    with pytest.raises(SessionError):
        Session(name=None)
    with pytest.raises(SessionError):
        Session(name="")


def test_session_singleton():
    session1a = Session(name="One")
    session1b = Session(name="One")
    session2a = Session(name="Two")
    session2b = Session(name="Two")

    assert session1a is session1b
    assert session2a is session2b

    assert session1a is not session2a
    assert session1a is not session2b
    assert session1b is not session2a
    assert session1b is not session2b


def test_session_settings():
    session1a = Session(name="One")
    session1b = Session(name="One")
    session2a = Session(name="Two")
    session2b = Session(name="Two")

    assert session1a.settings is session1b.settings
    assert session2a.settings is session2b.settings

    assert session1a.settings is not session2a.settings
    assert session1a.settings is not session2b.settings
    assert session1b.settings is not session2a.settings
    assert session1b.settings is not session2b.settings


def test_session_settings_values():
    session1 = Session(name="One")
    session2 = Session(name="Two")

    assert not session1.settings.autosave
    assert not session2.settings.autosave

    session1.settings.autosave = True

    assert session1.settings.autosave
    assert not session2.settings.autosave
