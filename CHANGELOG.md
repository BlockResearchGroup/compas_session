# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
