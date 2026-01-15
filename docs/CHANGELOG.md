# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CONTRIBUTING.md with contributor guidelines
- SECURITY.md with security reporting instructions
- `.env.example` for environment configuration template
- `.editorconfig` for consistent editor settings
- `pyproject.toml` with project configuration and pytest settings
- PR and issue templates for better contributor experience
- Dependabot configuration for automated dependency updates
- Improved CI/CD workflow with consolidated steps

### Changed
- Updated README.md with enhanced documentation
- Improved `.gitignore` with additional entries
- Consolidated CI workflows
- Reorganized repository layout into `daemons/`, `shared/`, `scripts/`, and `docs/`, with daemon runtime paths now anchored on `EDEN_ROOT` (repo root) and optional `EDEN_WORK_ROOT` for runtime outputs
- Removed binary artifacts from the repository (PDFs and a non-UTF8 XML)

### Fixed
- Pytest configuration to properly ignore duplicate folders
