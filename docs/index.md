# COMPAS Session

COMPAS Session provides persistent session objects for COMPAS workflows and
tools. A session groups arbitrary data, a COMPAS scene, settings, and recorded
history under one name.

The package offers two storage models:

- [`Session`][compas_session.session.Session] serializes the complete state to
  one JSON file and keeps one singleton per session name.
- [`LazyLoadSession`][compas_session.lazyload.LazyLoadSession] stores values in
  separate files below `<basedir>/<name>.session` and keeps one singleton per
  class.

Use session storage from one process at a time. The package does not provide
file locking or conflict resolution for concurrent writers.

## Next steps

- [Install the package](installation.md).
- Follow the [tutorial](tutorial.md).
- Browse the [API reference](reference/index.md).
