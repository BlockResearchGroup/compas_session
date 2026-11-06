from tempfile import TemporaryDirectory

from compas_session.session import Session

with TemporaryDirectory() as directory:
    session = Session(name="design", basedir=directory)
    session["iteration"] = 1
    session.dump()

    assert Session(name="design") is session
    assert session["iteration"] == 1
