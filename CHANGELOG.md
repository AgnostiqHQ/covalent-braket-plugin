# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

### Tests

- Enabled Codecov
- Added tests
- Update pre-commit hooks

## [0.4.1] - 2022-08-23

### Fixed

- Removed `--pre` from `pip install covalent` in Dockerfile

## [0.4.0] - 2022-08-17

### Changed

- Fixed `covalent` version to `stable` release

## [0.3.0] - 2022-08-16

### Added

- Updated required `covalent` version

## [0.2.0] - 2022-08-13

### Added

- Workflows needed for release

## [0.1.2] - 2022-08-10

### Fixed

- Dynamically set bucket name and repo name

### Docs

- Updated README with more getting started details

## [0.1.1] - 2022-08-08

### Fixed

- Dockerfile so that SAGEMAKER_PROGRAM is set correctly, removing ENTRYPOINT and CMD
- Pennylane version, upgraded to 0.24.0

## [0.1.0] - 2022-03-31

### Changed

- Changed global variable executor_plugin_name -> EXECUTOR_PLUGIN_NAME in executors to conform with PEP8.
