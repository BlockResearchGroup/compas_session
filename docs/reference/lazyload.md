# Lazy-load sessions

## Constructor

```python
LazyLoadSession(
    *,
    name: str | None = None,
    basedir: str | os.PathLike[str] | None = None,
    scene: Scene | None = None,
    settings: Settings | None = None,
    depth: int | None = None,
    delete_existing: bool = False,
)
```

- `name` identifies the session. If it is omitted, the first existing session
  directory or the base-directory name is used.
- `basedir` is the working directory containing the session directory. If it is
  omitted, the caller module's directory is used.
- `scene` and `settings` provide the initial scene and settings objects.
- `depth` sets the maximum retained history depth.
- `delete_existing` removes an existing session directory before creating the
  new session.

The class keeps one singleton instance. Constructing it again with a different
explicit name raises
[`SingletonError`][compas_session.lazyload.SingletonError].

## API

::: compas_session.lazyload.LazyLoadSession

::: compas_session.lazyload.SingletonError

::: compas_session.lazyload.LazyLoadSessionError
