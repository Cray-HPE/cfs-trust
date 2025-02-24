# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- CASMCMS-9292: When retrieving BSS global metadata, correctly pass in the key parameter.
- CASMCMS-9293: Use default values for `retries` and `backoff_factor`, instead of the current aggressive overrides

### Dependencies
- Require `requests-retry-session` 0.2.4, which has an important fix

## [1.7.5] - 2025-01-10
### Dependencies
- Change `requests_retry_session` version to avoid errors.

## [1.7.4] - 2024-09-05
### Dependencies
- CSM 1.6 moved to Kubernetes 1.24, so use client v24.x to ensure compatability
- CASMCMS-9135: Bump minimum `cray-services` base chart version from 10.0.5 to 11.0.0

## [1.7.3] - 2024-08-22
### Fixed
- Restore code accidentally removed from `connection.py` in v1.7.2

## [1.7.2] - 2024-08-16
### Changed
- Print list of installed Python modules after pip installs in Dockerfile, for logging purposes.

### Dependencies
- Instead of using `update_external_versions` to find the latest patch version of
  liveness, instead just pin the major/minor number directly in [`constraints.txt`](constraints.txt).
- Use `requests_retry_session` module instead of duplicating its code.

## [1.7.1] - 2024-06-28
### Changed
- When building unstable charts, have them point to the corresponding unstable Docker image
- Remove Randy Kleinman from the chart maintainer list; add Mitch Harding

### Dependencies
- CASMCMS-9006: Bump minimum `cray-services` base chart version from 7.0.0 to 10.0.5

## [1.7.0] - 2024-02-22
### Changed
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds

### Dependencies
- Bump `kubernetes` from 12.0.0 to 22.6.0 to match CSM 1.6 Kubernetes version

## [1.6.8] - 2023-08-10
### Changed
- Disabled concurrent Jenkins builds on same branch/commit
- Added build timeout to avoid hung builds
- RPM OS type changed to `noos`

## [1.6.7] - 2023-07-25
### Dependencies
- Use `update_external_versions` to get latest patch version of `liveness` Python module.
- Bumped dependency patch versions:
| Package                  | From     | To       |
|--------------------------|----------|----------|
| `cachetools`             | 4.2.1    | 4.2.4    |
| `oauthlib`               | 3.1.0    | 3.1.1    |
| `python-dateutil`        | 2.8.1    | 2.8.2    |
| `requests-oauthlib`      | 1.3.0    | 1.3.1    |
| `rsa`                    | 4.7      | 4.7.2    |
| `urllib3`                | 1.26.2   | 1.26.16  |

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
