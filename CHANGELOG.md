# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]


### Changed

- Updated Dockerfile to contain `COVALENT_BASE_IMAGE` ARG
- Removed explicit cloudpickle install due to version conflict with covalent cloudpickle from Dockerfile
- Constrained covalent semver range to be less than major version 1 for this version of Dockerfile

### Documentation

- Update README to include reference to new `ecr_image_uri` key


## [0.8.0] - 2022-10-25

### Changed

- Updated executor to use pre-built braket executor base image
- Updated aws plugins to be gt than 0.7.0rc0

## [0.7.2] - 2022-10-06

### Fixed

- License checker reference.

### Operations

- Added license workflow

## [0.7.1] - 2022-10-06

### Fixed

- Store `BASE_COVALENT_AWS_PLUGINS_ONLY` in a temporary file rather than storing it as an environment variable.

### Docs

- Simplified README

## [0.7.0] - 2022-09-30

### Added

-  Logic to specify that only the base covalent-aws-plugins package is to be installed.

## [0.6.1] - 2022-09-20

### Fixed

- Getting default values from config file if not defined in class instance

## [0.6.0] - 2022-09-16

### Changed

- Updated requirements.txt to pin aws executor plugins to pre-release version 0.1.0rc0

## [0.5.0] - 2022-09-15

### Changed

- BraketExecutor is now derived from AWSExecutor

### Tests

- Enabled Codecov
- Added tests
- Update pre-commit hooks
- Updated some tests to be async aware

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
