from compas_session.settings import Settings


def test_autosave():
    settings = Settings()
    assert settings.autosave is True
    settings.autosave = False
    assert settings.autosave is False
