# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased
### Dependencies
- Use `update_external_versions` to get latest patch version of `liveness` Python module.

## [1.6.6] - 2023-07-18
### Dependencies
- Bump `PyYAML` from 5.4.1 to 6.0.1 to avoid build issue caused by https://github.com/yaml/pyyaml/issues/601

## [1.6.5] - 2023-06-22
### Added
- Build SLES SP5 RPM

## [1.6.4] - 2023-05-17
### Changed
- Switched rpm build to `noarch`
### Removed
- Removed defunct files leftover from previous versioning system

## [1.6.3] - 2022-12-20
### Added
- Add Artifactory authentication to Jenkinsfile

## [1.6.2] - 2022-12-02
### Added
- Authenticate to CSM's artifactory

### Changed
- Spelling corrections.

## [1.5.1] - 2022-08-18
### Fixed
- Escalated pod priority so that configuration has a better chance of running when a node is cordoned

## [1.5.0] - 2022-07-14
### Added
- Support for SLES SP4

### Changed
- Convert to gitflow/gitversion.
