from compas.geometry import Point
from compas_session.lazyload import LazyLoadSession
from compas_session.session import Session


def test_session_roundtrip_preserves_compas_data(tmp_path):
    session = Session(name="roundtrip", basedir=tmp_path)
    point = Point(1.0, 2.0, 3.0)
    session["point"] = point

    session.dump()
    session.data = {}
    session.load()

    restored = session["point"]
    assert isinstance(restored, Point)
    assert restored == point

    stored = session.get_from_file(tmp_path / "roundtrip.json", name="data")
    assert isinstance(stored["point"], Point)
    assert stored["point"] == point


def test_lazy_session_rehydrates_compas_data_and_history(tmp_path):
    point = Point(1.0, 2.0, 3.0)
    session = LazyLoadSession(name="roundtrip", basedir=tmp_path)
    session["point"] = point
    session.record("initial point")
    session.dump_history()

    LazyLoadSession.delete_instance()
    restored_session = LazyLoadSession(name="roundtrip", basedir=tmp_path)
    restored = restored_session["point"]

    assert isinstance(restored, Point)
    assert restored == point
    assert restored_session.history == session.history
    assert isinstance(restored_session.history[0], tuple)
    assert restored_session.current == session.current
