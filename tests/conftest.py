"""Pytest configuration and shared fixtures for tikz_extractor tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_tikz_content():
    """Sample TikZ content for testing."""
    return {
        'simple': r'\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}',
        'complex': r'''\begin{tikzpicture}[scale=2]
\draw[thick,->] (0,0) -- (2,0) node[anchor=north west] {x axis};
\draw[thick,->] (0,0) -- (0,2) node[anchor=south east] {y axis};
\draw (0,0) circle (1);
\end{tikzpicture}''',
        'with_options': r'\begin{tikzpicture}[scale=0.5,transform shape]\node at (0,0) {Hello};\end{tikzpicture}',
        'multiline': r'''\begin{tikzpicture}
\coordinate (A) at (0,0);
\coordinate (B) at (1,1);
\draw (A) -- (B);
\end{tikzpicture}'''
    }


@pytest.fixture
def sample_files_content():
    """Sample file contents with various TikZ scenarios."""
    return {
        'single_tikz.tex': r'''
\documentclass{article}
\usepackage{tikz}
\begin{document}
Some text before.
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\end{tikzpicture}
Some text after.
\end{document}
''',
        'multiple_tikz.tex': r'''
\documentclass{article}
\usepackage{tikz}
\begin{document}
First diagram:
\begin{tikzpicture}
\draw (0,0) circle (1);
\end{tikzpicture}

Second diagram:
\begin{tikzpicture}[scale=2]
\draw[thick] (0,0) -- (1,1);
\end{tikzpicture}
\end{document}
''',
        'no_tikz.tex': r'''
\documentclass{article}
\begin{document}
This file has no TikZ content.
Just regular LaTeX text.
\end{document}
''',
        'tikz_in_markdown.md': r'''# My Document

Here's some TikZ in markdown:

```latex
\begin{tikzpicture}
\node at (0,0) {Markdown TikZ};
\end{tikzpicture}
```

And some regular text.
''',
        'tikz_in_python.py': r'''"""
Python file with TikZ in docstring.
"""

def generate_tikz():
    """Generate TikZ code.
    
    Example:
    \begin{tikzpicture}
    \draw (0,0) -- (1,1);
    \end{tikzpicture}
    """
    return "tikz code"
''',
        'empty_file.tex': '',
        'nested_tikz.tex': r'''
\documentclass{article}
\usepackage{tikz}
\begin{document}
\begin{tikzpicture}
\draw (0,0) -- (1,1);
\begin{scope}[shift={(2,0)}]
\draw (0,0) circle (0.5);
\end{scope}
\end{tikzpicture}
\end{document}
''',
        'malformed_tikz.tex': r'''
\documentclass{article}
\begin{document}
\begin{tikzpicture}
\draw (0,0) -- (1,1);
% Missing \end{tikzpicture}

\begin{tikzpicture}
\draw (0,0) circle (1);
\end{tikzpicture}
\end{document}
'''
    }


@pytest.fixture
def test_file_structure(temp_dir, sample_files_content):
    """Create a test directory structure with sample files."""
    # Create main test files
    for filename, content in sample_files_content.items():
        file_path = temp_dir / filename
        file_path.write_text(content, encoding='utf-8')
    
    # Create nested directory structure
    nested_dir = temp_dir / 'nested' / 'deep'
    nested_dir.mkdir(parents=True)
    
    # Add files in nested directories
    (nested_dir / 'deep_tikz.tex').write_text(r'''
\begin{tikzpicture}
\draw (0,0) -- (2,2);
\end{tikzpicture}
''', encoding='utf-8')
    
    (temp_dir / 'nested' / 'mid_level.md').write_text(r'''
# Mid Level File

\begin{tikzpicture}
\node {Mid level};
\end{tikzpicture}
''', encoding='utf-8')
    
    # Create files with different extensions
    (temp_dir / 'other.txt').write_text('No TikZ here', encoding='utf-8')
    (temp_dir / 'script.sh').write_text('#!/bin/bash\necho "hello"', encoding='utf-8')
    
    return temp_dir


@pytest.fixture
def expected_metadata_structure():
    """Expected structure for metadata dictionaries."""
    return {
        'source': str,
        'out_path': str,
        'index': int,
        'content': str
    }


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing AI context generation."""
    return [
        {
            'source': '/path/to/source1.tex',
            'out_path': '/path/to/output/source1__tikz1.tex',
            'index': 1,
            'content': r'\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}'
        },
        {
            'source': '/path/to/source2.md',
            'out_path': '/path/to/output/source2__tikz1.tex',
            'index': 1,
            'content': r'\begin{tikzpicture}\node {Hello};\end{tikzpicture}'
        }
    ]


@pytest.fixture
def unreadable_file(temp_dir):
    """Create an unreadable file for error handling tests."""
    unreadable_path = temp_dir / 'unreadable.tex'
    unreadable_path.write_text('Some content', encoding='utf-8')
    # Make file unreadable (this might not work on all systems)
    try:
        unreadable_path.chmod(0o000)
        yield unreadable_path
        unreadable_path.chmod(0o644)  # Restore permissions for cleanup
    except (OSError, PermissionError):
        # If we can't change permissions, just yield a regular file
        yield unreadable_path


@pytest.fixture
def binary_file(temp_dir):
    """Create a binary file that should cause encoding errors."""
    binary_path = temp_dir / 'binary.tex'
    # Write some binary data that will cause UTF-8 decoding errors
    with open(binary_path, 'wb') as f:
        f.write(b'\x80\x81\x82\x83\x84\x85')
    return binary_path