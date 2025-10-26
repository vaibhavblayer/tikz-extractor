# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.2.5] - 2024-12-26

### Changed
- Updated GitHub Actions workflow to trigger on tag pushes for automatic PyPI publishing

## [0.2.4] - 2024-12-26

### Fixed
- Fixed CLI filename collision bug where multiple TikZ blocks would overwrite each other
- Added proper global counter tracking across files in CLI extraction
- Improved TikZ content formatting with consistent indentation in both individual files and AI context

### Changed
- Simplified output filenames to use `tikz_N.tex` format for cleaner naming
- Enhanced AI context file format with consistent TikZ block formatting

## [0.1.0] - 2024-01-XX

### Added
- **Core Extraction Engine**
  - Recursive directory scanning with configurable file extensions
  - Robust TikZ block extraction using compiled regex patterns
  - Cross-platform filename sanitization for output files
  - Comprehensive error handling for encoding and I/O issues

- **Command-Line Interface**
  - `tikz-extract` command with flexible options
  - Support for custom source and output directories
  - Configurable file extension filtering
  - Dry-run mode for previewing extraction results
  - Verbose output for detailed processing information
  - AI context file generation for LLM consumption

- **Python Module Interface**
  - Importable package for programmatic usage
  - Clean API with well-documented functions
  - Type hints for all public functions
  - Comprehensive docstrings with usage examples

- **File Processing Features**
  - Individual .tex file generation for each TikZ block
  - Descriptive filename generation based on source paths
  - Structured metadata collection for each extracted block
  - AI context file with formatted headers and separators

- **Testing and Quality Assurance**
  - Comprehensive test suite with pytest
  - Unit tests for all core functions
  - Integration tests for complete workflows
  - CLI integration tests with argument validation
  - Edge case and error handling tests
  - Test fixtures with sample TikZ content

- **Development Infrastructure**
  - Poetry-based dependency management
  - GitHub Actions CI/CD pipeline
  - Multi-platform testing (Linux, macOS, Windows)
  - Multi-version Python support (3.10, 3.11, 3.12)
  - Code quality checks (Black, isort, flake8, mypy)
  - Security scanning (safety, bandit)
  - Automated PyPI publishing on releases

- **Documentation**
  - Comprehensive README with installation and usage instructions
  - API reference with detailed function documentation
  - CLI parameter documentation with examples
  - Contributing guidelines for developers
  - Code of conduct and development setup instructions

- **Package Configuration**
  - Complete pyproject.toml with metadata and dependencies
  - Tool configurations for development tools
  - MIT license for open source distribution
  - Semantic versioning and changelog tracking

### Technical Details
- **Dependencies**: Minimal external dependencies (Click for CLI)
- **Python Support**: Python 3.10+ with type hints throughout
- **Regex Pattern**: Multi-line TikZ block matching with DOTALL flag
- **Error Recovery**: Graceful handling of unreadable files and encoding issues
- **Cross-Platform**: Windows, macOS, and Linux compatibility
- **Performance**: Efficient directory traversal and compiled regex patterns

### Known Limitations
- Currently supports only standard TikZ picture environments
- UTF-8 encoding assumed for text files
- No support for nested or custom TikZ environments
- Limited to file-based processing (no direct string input via CLI)

---

## Version History Format

Each version entry should include:

### Added
- New features and functionality

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes and corrections

### Security
- Security-related changes and fixes

---

## Contributing to the Changelog

When contributing changes:

1. Add your changes to the `[Unreleased]` section
2. Use the appropriate category (Added, Changed, Fixed, etc.)
3. Write clear, concise descriptions
4. Include issue/PR references when applicable
5. Follow the existing format and style

Example entry:
```markdown
### Added
- New `--pattern` option for custom TikZ pattern matching (#123)
- Support for nested TikZ environments in extraction (#145)

### Fixed
- Fixed encoding detection for non-UTF-8 files (#134)
- Resolved path handling issue on Windows (#156)
```

## Release Process

1. Move items from `[Unreleased]` to a new version section
2. Update the version number in `pyproject.toml`
3. Create a git tag with the version number
4. Create a GitHub release with changelog content
5. Automated CI/CD will handle PyPI publishing