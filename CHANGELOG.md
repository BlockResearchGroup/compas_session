# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

* Added `compas_session.lazyload.LazyLoadSession.datadirname`.
* Added `compas_session.lazyload.LazyLoadSession.recordsdirname`.
* Added `compas_session.lazyload.LazyLoadSession.tempdirname`.
* Added `compas_session.lazyload.LazyLoadSession.historyfilename`.
* Added `compas_session.lazyload.LazyLoadSession.settingsfilename`.
* Added `compas_session.lazyload.LazyLoadSession.versionfilename`.
* Added `compas_session.lazyload.LazyLoadSession.tolerancefilename`.
* Added `compas_session.lazyload.LazyLoadSession.load_tolerance`.
* Added `compas_session.lazyload.LazyLoadSession.dump_tolerance`.
* Added `compas_session.lazyload.LazyLoadSession.load_settings`.
* Added `compas_session.lazyload.LazyLoadSession.dump_settings`.
* Added `compas_session.lazyload.LazyLoadSession.load_scene`.
* Added `compas_session.lazyload.LazyLoadSession.dump_scene`.
* Added `compas_session.lazyload.LazyLoadSession.load_history`.
* Added `compas_session.lazyload.LazyLoadSession.dump_history`.
* Added `compas_session.lazyload.LazyLoadSession.load_tolerance`.
* Added `compas_session.lazyload.LazyLoadSession.undo`.
* Added `compas_session.lazyload.LazyLoadSession.redo`.

### Changed

### Removed


## [0.5.5] 2025-06-06

### Added

### Changed

* Fix bug in `compas_session.session.Session.record` due to unwritable tempdir.

### Removed


## [0.5.4] 2025-05-31

### Added

### Changed

* Changed session "name" to be an optional parameter. Name of the parent directory is used when no other name is provided.

### Removed


## [0.5.3] 2025-05-31

### Added

### Changed

* Changed tolerance support to implicit implementation.

### Removed


## [0.5.2] 2025-05-31

### Added

* Added support for session tolerance.

### Changed

### Removed


## [0.5.1] 2025-05-30

### Added

### Changed

* Changed `compas_session.lazyload.LazyLoadSession.get(..., filepath=...)` to convert path to a string before passing on to the constructors for compatibility with Rhino.

### Removed


## [0.5.0] 2025-05-30

### Added

* Added `compas_session.lazyload.LazyLoadSession`.
* Added `tests/test_lazy.py`.

### Changed

### Removed

## [0.4.5] 2024-11-10

### Added

### Changed

* Changed requirements to work better with Rhino pip.

### Removed

## [0.4.1] 2024-10-28

### Added

### Changed

* Fixed bug in `compas_session.session.Session.load()` due to unintentional resetting.

### Removed

## [0.4.0] 2024-10-24

### Added

* Added `pydantic` as requirement.
* Added `compas_session.settings.Settings` based on `pydantic.BaseModel`.
* Added `compas_session.session.Session.scene` as default scene.
* Added `compas_session.session.Session.settings` as default settings.

### Changed

* Changed `compas_session.namedsession.NamedSession` to `compas_session.session.Session`.
* Changed serialisation dict of session to `{"data": ..., "scene": ..., "settings": ...}`.

### Removed

* Removed `compas.scene.Scene` from `compas_session.session.Session.data`.

## [0.3.0] 2024-10-23

### Added

### Changed

* Fixed bug related to missing `kwargs` in `compas_session.namedsession.NamedSession.__new__`.

### Removed

## [0.2.0] 2024-10-01

### Added

* Added `compas_session.namedsession.NamedSession`

### Changed

### Removed
