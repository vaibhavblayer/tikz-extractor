# Contributing to TikZ Extractor

Thank you for your interest in contributing to TikZ Extractor! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Poetry for dependency management
- Git for version control

### Setting up the Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vaibhavblayer/tikz-extractor.git
   cd tikz-extractor
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install --with dev
   ```

4. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

5. **Verify the installation:**
   ```bash
   poetry run pytest
   poetry run tikz-extract --help
   ```

## Development Workflow

### Making Changes

1. **Create a new branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the coding standards below.

3. **Run tests and linting:**
   ```bash
   # Run all tests
   poetry run pytest

   # Run tests with coverage
   poetry run pytest --cov=tikz_extractor

   # Format code
   poetry run black tikz_extractor tests

   # Sort imports
   poetry run isort tikz_extractor tests

   # Lint code
   poetry run flake8 tikz_extractor tests

   # Type checking
   poetry run mypy tikz_extractor
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature" # or "fix: resolve bug"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for custom TikZ patterns
fix: handle encoding errors in file processing
docs: update README with new CLI options
test: add edge case tests for file discovery
```

## Coding Standards

### Python Code Style

- **Formatting:** Use Black with default settings (88 character line length)
- **Import sorting:** Use isort with Black-compatible profile
- **Linting:** Follow flake8 rules with project-specific configuration
- **Type hints:** Use type hints for all function parameters and return values
- **Docstrings:** Write comprehensive docstrings following Google style

### Code Quality Guidelines

1. **Functions should be focused and do one thing well**
2. **Use descriptive variable and function names**
3. **Keep functions reasonably short (generally < 50 lines)**
4. **Handle errors gracefully with appropriate exception handling**
5. **Write comprehensive docstrings with examples**
6. **Include type hints for all public functions**

### Example Code Style

```python
from pathlib import Path
from typing import List, Dict, Optional


def extract_tikz_from_text(text: str) -> List[str]:
    """Extract TikZ blocks from text using regex pattern matching.
    
    Args:
        text (str): Text content to search for TikZ blocks.
        
    Returns:
        List[str]: List of complete TikZ block strings found in the text.
        
    Example:
        >>> content = "\\begin{tikzpicture}\\draw (0,0) -- (1,1);\\end{tikzpicture}"
        >>> blocks = extract_tikz_from_text(content)
        >>> len(blocks)
        1
    """
    return TIKZ_RE.findall(text)
```

## Testing

### Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and configuration
├── test_extractor.py     # Core extraction function tests
├── test_cli.py          # CLI interface tests
├── test_integration.py  # End-to-end integration tests
└── test_edge_cases.py   # Edge case and error handling tests
```

### Writing Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow the Arrange-Act-Assert pattern**
3. **Test both success and failure cases**
4. **Use fixtures for common test data**
5. **Mock external dependencies when appropriate**

### Test Example

```python
def test_extract_tikz_from_text_single_block():
    """Test extraction of a single TikZ block from text."""
    # Arrange
    content = """
    Some text here
    \\begin{tikzpicture}
    \\draw (0,0) -- (1,1);
    \\end{tikzpicture}
    More text
    """
    
    # Act
    blocks = extract_tikz_from_text(content)
    
    # Assert
    assert len(blocks) == 1
    assert "\\begin{tikzpicture}" in blocks[0]
    assert "\\end{tikzpicture}" in blocks[0]
    assert "\\draw (0,0) -- (1,1);" in blocks[0]
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_extractor.py

# Run with coverage
poetry run pytest --cov=tikz_extractor --cov-report=html

# Run tests in verbose mode
poetry run pytest -v

# Run tests matching a pattern
poetry run pytest -k "test_extract"
```

## Documentation

### Docstring Guidelines

- Use Google-style docstrings
- Include type information in Args and Returns sections
- Provide usage examples when helpful
- Document exceptions that may be raised

### README Updates

When adding new features:
1. Update the feature list in README.md
2. Add usage examples if applicable
3. Update the API reference section
4. Add any new CLI parameters to the parameter table

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass:** `poetry run pytest`
2. **Ensure code is properly formatted:** `poetry run black tikz_extractor tests`
3. **Ensure imports are sorted:** `poetry run isort tikz_extractor tests`
4. **Ensure linting passes:** `poetry run flake8 tikz_extractor tests`
5. **Ensure type checking passes:** `poetry run mypy tikz_extractor`
6. **Update documentation** if needed
7. **Add tests** for new functionality

### Pull Request Guidelines

1. **Provide a clear description** of what the PR does
2. **Reference any related issues** using "Fixes #123" or "Closes #123"
3. **Include screenshots** if the change affects CLI output
4. **Update CHANGELOG.md** with your changes
5. **Ensure CI passes** before requesting review

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Python version** and operating system
2. **Package version** (`tikz-extract --version`)
3. **Steps to reproduce** the issue
4. **Expected behavior** vs actual behavior
5. **Sample files** or content that triggers the bug (if applicable)
6. **Full error messages** and stack traces

### Feature Requests

When requesting features:

1. **Describe the use case** and why the feature would be valuable
2. **Provide examples** of how the feature would be used
3. **Consider backwards compatibility** implications
4. **Suggest implementation approaches** if you have ideas

## Code of Conduct

### Our Standards

- **Be respectful** and inclusive in all interactions
- **Be constructive** in feedback and discussions
- **Focus on the code and ideas**, not personal attributes
- **Help others learn** and grow in their contributions

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information without permission
- Any conduct that would be inappropriate in a professional setting

## Getting Help

- **GitHub Issues:** For bug reports and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Code Review:** Feel free to ask for feedback on your contributions

## Recognition

Contributors will be recognized in:
- The project's README.md file
- Release notes for significant contributions
- GitHub's contributor statistics

Thank you for contributing to TikZ Extractor! 🎉