from pydantic import BaseModel


class Settings(BaseModel):
    """Persistent session settings.

    Attributes
    ----------
    autosave
        Whether a client should save session state automatically.
    autosync
        Whether lazy-load session values are written when they are set.

    Examples
    --------
    >>> settings = Settings(autosync=False)
    >>> settings.autosave
    False
    >>> settings.autosync
    False

    """

    autosave: bool = False
    autosync: bool = True
