from compas_session.lazyload import LazyLoadSession
from compas_session.session import Session


Session()  # expected-error: reportCallIssue
Session(name="example", basedir=1)  # expected-error: reportArgumentType
LazyLoadSession(depth="3")  # expected-error: reportArgumentType
LazyLoadSession(scene=object())  # expected-error: reportArgumentType
LazyLoadSession(settings=object())  # expected-error: reportArgumentType
