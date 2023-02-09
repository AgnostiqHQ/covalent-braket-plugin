# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [UNRELEASED]

## [0.22.0] - 2023-02-09

### Added

- Adding `repository_dispatch` trigger to build base executor image from core covalent

## [0.21.2] - 2023-02-09

### Fixed

- Second attempt at fixing tests.yml workflow.

## [0.21.1] - 2023-02-07

### Fixed

- tests.yml workflow.

## [0.21.0] - 2023-01-19

### Changed

- Updated docker workflow to allow manual pre-release base executor image release
- Minor updates for consistency with other docker workflows

## [0.20.1] - 2023-01-18

### Fixed

- Fixed Dockerfile and docker workflow syntax to build pre-release base executor images

## [0.20.0] - 2023-01-07

### Changed

- Updated docker workflow to specify pre-release flag as a build arg

## [0.19.0] - 2023-01-06

### Changed

- Ability to specify covalent version in docker workflow

## [0.18.3] - 2023-01-06

### Fixed

- Fixed COVALENT_BASE_IMAGE arg in docker workflow quotations

## [0.18.2] - 2023-01-06

### Fixed

- Fixed COVALENT_BASE_IMAGE arg in docker workflow

## [0.18.1] - 2023-01-06

### Fixed

- Fixed docker workflow github event name syntax

## [0.18.0] - 2023-01-06

### Changed

- Removed inputs.version from checkout step in docker workflow

## [0.17.3] - 2023-01-06

### Fixed

- Added id-token write, and permissions for OIDC to push to ECR from role

## [0.17.2] - 2023-01-06

### Fixed

- Fixed `typo` in action spelling

## [0.17.1] - 2023-01-06

### Fixed

- Updated version of the `docker` buildx actions

## [0.17.0] - 2023-01-06

### Changed

- Updated docker workflow to create manual pre-releases in addition to stable version

## [0.16.0] - 2023-01-06

### Operations

### Added

- Adding `docker.yml` workflow to build and release braket executor docker image

### Changed

- Removed explicit `covalent` installation in the Docker and use base `covalent` image from public registry
- Invoke `docker.yml` from `release.yml` via a workflow call

## [0.15.0] - 2022-12-15

### Changed

- Removed references to `.env` file in the functional test README.

## [0.14.0] - 2022-12-06

### Changed

- Using executor aliases instead of classes for functional tests

## [0.13.0] - 2022-11-22

### Changed

- Removed executor defaults for boto3 session args, added .env.example

## [0.12.0] - 2022-11-10

### Changed

- Functional tests using pytest and .env file configuration

## [0.11.0] - 2022-10-28

### Changed

- Bumped aws plugins version to new stable release

## [0.10.0] - 2022-10-27

### Changed

- Added Alejandro to paul blart group

## [0.9.0] - 2022-10-27


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
