# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### [0.2.4] - 2025-11-21
### Changed
- Fix `README.md` not shown in PyPI page.

### [0.2.3] - 2025-11-20
### Added
- Download button (💾) next to copy button using `<a download>` tag
  - In Jupyter: Downloads image to browser's default download folder
  - In VS Code: Opens image in new browser tab

### Changed
- Refactored code structure by extracting JavaScript/HTML templates to `_templates.py` module

### [0.2.2] - 2025-11-20
### Added
- JavaScript-based copy button overlay on all matplotlib images for one-click clipboard copy functionality
- Optional development dependencies (`jupyter`, `ipykernel`, `pytest`) via `[project.optional-dependencies]`

### Changed
- Removed unnecessary `uv` workspace configuration from `pyproject.toml`

### [0.2.1] - 2025-10-10
### Fixed
- Fix `dietnb install` not working bug.

### [0.2.0] - 2025-10-10
### Added
- Relative image path support so notebooks and image folders can be moved together without breaking `<img>` tags.
- Comprehensive multi-shell test suite covering Terminal, ZMQ, embedded, and Qt in-process IPython shells.

### Changed
- Simplified runtime dependencies to `ipython>=8` and `matplotlib>=3.5`, and documented Qt Console packages inside the `dev` optional dependency group.
- README documents updated to describe relative path handling and execution registry cleanup.

### Fixed
- Stale image cleanup now keyed by directory and cell execution, preventing residual PNG files after reruns.

### [0.1.7] - 2025-06-05
### Changed
- Filename format changed from `{key}_{idx}_{exec_count}.png` to `{exec_count}_{idx}_{key}.png`

## [0.1.6] - 2025-05-09
### Changed
- Fix bug due to project directory changed
- Resolving compatibility between VSC and web jupyter notebooks

## [0.1.5] - 2025-05-09
### Changed
- Fix bug on `jupyter notebook` environment

## [0.1.4] - 2025-05-08
### Changed
- Updated `README.md`.

## [0.1.3] - 2025-05-08 
### Added
- Added `dietnb uninstall` command to remove the startup script.
- Established `dev` and `release` branch strategy for git workflow.
- Created `CHANGELOG.md` to document project changes.