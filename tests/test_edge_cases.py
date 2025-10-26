"""Edge case and error handling tests for tikz_extractor."""

import shutil
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from tikz_extractor import extractor
from tikz_extractor.cli import cli


class TestEmptyDirectoriesAndFiles:
    """Test handling of empty directories and files without TikZ blocks."""

    def test_extract_from_empty_directory(self, temp_dir):
        """Test extraction from completely empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        out_dir = temp_dir / "output"

        metadata = extractor.extract_from_directory(empty_dir, out_dir, [".tex", ".md"])

        assert len(metadata) == 0
        # Output directory might be created by write_extracted_blocks even with no blocks

    def test_extract_from_directory_with_empty_files(self, temp_dir):
        """Test extraction from directory with empty files."""
        # Create empty files
        (temp_dir / "empty1.tex").write_text("", encoding="utf-8")
        (temp_dir / "empty2.md").write_text("", encoding="utf-8")
        (temp_dir / "empty3.py").write_text("", encoding="utf-8")

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(
            temp_dir, out_dir, [".tex", ".md", ".py"]
        )

        assert len(metadata) == 0

    def test_extract_from_files_without_tikz(self, temp_dir):
        """Test extraction from files that don't contain TikZ blocks."""
        # Create files with various content but no TikZ
        (temp_dir / "latex_no_tikz.tex").write_text(
            r"""
        \documentclass{article}
        \begin{document}
        This is just regular LaTeX content.
        No TikZ pictures here.
        \end{document}
        """,
            encoding="utf-8",
        )

        (temp_dir / "markdown_no_tikz.md").write_text(
            """
        # Markdown File
        
        This is just regular markdown content.
        No TikZ blocks here.
        """,
            encoding="utf-8",
        )

        (temp_dir / "python_no_tikz.py").write_text(
            """
        def hello():
            print("Hello world")
            return "No TikZ here"
        """,
            encoding="utf-8",
        )

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(
            temp_dir, out_dir, [".tex", ".md", ".py"]
        )

        assert len(metadata) == 0

    def test_cli_with_empty_directory(self, temp_dir):
        """Test CLI behavior with empty directory."""
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--src", str(temp_dir), "--verbose"])

            assert result.exit_code == 0
            assert "No files found matching the specified extensions" in result.output


class TestMultipleTikzBlocks:
    """Test handling of files with multiple TikZ blocks and nested environments."""

    def test_extract_multiple_tikz_blocks_same_file(self, temp_dir):
        """Test extracting multiple TikZ blocks from the same file."""
        content = r"""
        \documentclass{article}
        \usepackage{tikz}
        \begin{document}
        
        First diagram:
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \end{tikzpicture}
        
        Some text in between.
        
        Second diagram:
        \begin{tikzpicture}[scale=2]
        \draw (0,0) circle (1);
        \end{tikzpicture}
        
        Third diagram:
        \begin{tikzpicture}
        \node at (0,0) {Hello};
        \node at (1,1) {World};
        \end{tikzpicture}
        
        \end{document}
        """

        (temp_dir / "multiple.tex").write_text(content, encoding="utf-8")

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        # Should find exactly 3 TikZ blocks
        assert len(metadata) == 3

        # Check that indices are correct
        indices = [meta["index"] for meta in metadata]
        assert indices == [1, 2, 3]

        # Check that all blocks are different
        contents = [meta["content"] for meta in metadata]
        assert len(set(contents)) == 3  # All unique

        # Verify each block is complete
        for content in contents:
            assert content.startswith(r"\begin{tikzpicture}")
            assert content.strip().endswith(r"\end{tikzpicture}")

    def test_extract_nested_tikz_environments(self, temp_dir):
        """Test extracting TikZ blocks with nested environments."""
        content = r"""
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \begin{scope}[shift={(2,0)}]
        \draw (0,0) circle (0.5);
        \begin{scope}[scale=0.5]
        \draw (0,0) -- (1,1);
        \end{scope}
        \end{scope}
        \end{tikzpicture}
        """

        (temp_dir / "nested.tex").write_text(content, encoding="utf-8")

        blocks = extractor.extract_tikz_from_text(content)

        assert len(blocks) == 1
        assert r"\begin{scope}" in blocks[0]
        assert r"\end{scope}" in blocks[0]
        assert blocks[0].count(r"\begin{scope}") == 2
        assert blocks[0].count(r"\end{scope}") == 2

    def test_extract_tikz_with_complex_options(self, temp_dir):
        """Test extracting TikZ blocks with complex options and parameters."""
        content = r"""
        \begin{tikzpicture}[
            scale=2,
            every node/.style={draw, circle, minimum size=1cm},
            every edge/.style={draw, thick, ->}
        ]
        \node (A) at (0,0) {A};
        \node (B) at (2,0) {B};
        \draw (A) -- (B);
        \end{tikzpicture}
        """

        blocks = extractor.extract_tikz_from_text(content)

        assert len(blocks) == 1
        assert "scale=2" in blocks[0]
        assert "every node/.style" in blocks[0]
        assert "every edge/.style" in blocks[0]

    def test_extract_tikz_blocks_with_comments(self, temp_dir):
        """Test extracting TikZ blocks that contain LaTeX comments."""
        content = r"""
        \begin{tikzpicture}
        % This is a comment
        \draw (0,0) -- (1,1); % Another comment
        % More comments
        \node at (0.5,0.5) {Text};
        \end{tikzpicture}
        """

        blocks = extractor.extract_tikz_from_text(content)

        assert len(blocks) == 1
        assert "% This is a comment" in blocks[0]
        assert "% Another comment" in blocks[0]


class TestErrorRecovery:
    """Test error recovery for unreadable files and encoding issues."""

    def test_extract_with_encoding_errors(self, temp_dir, binary_file):
        """Test that extraction continues when encountering encoding errors."""
        # Create a good file alongside the binary file
        (temp_dir / "good.tex").write_text(
            r"""
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \end{tikzpicture}
        """,
            encoding="utf-8",
        )

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        # Should find the TikZ block from the good file, skip the binary file
        assert len(metadata) == 1
        assert "good.tex" in metadata[0]["source"]

    def test_extract_with_permission_errors(self, temp_dir):
        """Test handling of files with permission errors."""
        # Create a good file
        (temp_dir / "good.tex").write_text(
            r"""
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \end{tikzpicture}
        """,
            encoding="utf-8",
        )

        # Create a file and try to make it unreadable
        unreadable_file = temp_dir / "unreadable.tex"
        unreadable_file.write_text("Some content", encoding="utf-8")

        try:
            unreadable_file.chmod(0o000)  # Remove all permissions

            out_dir = temp_dir / "output"
            metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

            # Should find the TikZ block from the good file, skip the unreadable file
            assert len(metadata) == 1
            assert "good.tex" in metadata[0]["source"]

        except (OSError, PermissionError):
            # If we can't change permissions (e.g., on some systems), skip this test
            pytest.skip("Cannot change file permissions on this system")
        finally:
            # Restore permissions for cleanup
            try:
                unreadable_file.chmod(0o644)
            except (OSError, PermissionError):
                pass

    def test_extract_with_mixed_file_errors(self, temp_dir):
        """Test extraction with a mix of good files, encoding errors, and permission errors."""
        # Create several good files
        (temp_dir / "good1.tex").write_text(
            r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}",
            encoding="utf-8",
        )
        (temp_dir / "good2.tex").write_text(
            r"\begin{tikzpicture}\draw (0,0) circle (1);\end{tikzpicture}",
            encoding="utf-8",
        )

        # Create a binary file (encoding error)
        with open(temp_dir / "binary.tex", "wb") as f:
            f.write(b"\x80\x81\x82\x83")

        # Create an empty file (no TikZ)
        (temp_dir / "empty.tex").write_text("", encoding="utf-8")

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        # Should find 2 TikZ blocks from the good files
        assert len(metadata) == 2
        sources = [meta["source"] for meta in metadata]
        assert any("good1.tex" in source for source in sources)
        assert any("good2.tex" in source for source in sources)

    def test_cli_error_recovery_with_verbose(self, temp_dir):
        """Test CLI error recovery with verbose output showing skipped files."""
        # Create good and bad files
        (temp_dir / "good.tex").write_text(
            r"\begin{tikzpicture}\draw (0,0) -- (1,1);\end{tikzpicture}",
            encoding="utf-8",
        )

        with open(temp_dir / "binary.tex", "wb") as f:
            f.write(b"\x80\x81\x82\x83")

        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["--src", str(temp_dir), "--verbose"])

            assert result.exit_code == 0
            assert "Successfully found TikZ content" in result.output
            # The verbose output should show processing details


class TestMalformedTikzContent:
    """Test handling of malformed or incomplete TikZ content."""

    def test_extract_incomplete_tikz_blocks(self, temp_dir):
        """Test extraction from files with incomplete TikZ blocks."""
        content = r"""
        \documentclass{article}
        \begin{document}
        
        This has an incomplete TikZ block:
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        % Missing \end{tikzpicture}
        
        This has a complete one:
        \begin{tikzpicture}
        \draw (0,0) circle (1);
        \end{tikzpicture}
        
        \end{document}
        """

        blocks = extractor.extract_tikz_from_text(content)

        # The regex will actually match both blocks since it's greedy
        # The incomplete block will match from \begin{tikzpicture} to the next \end{tikzpicture}
        assert len(blocks) >= 1
        # At least one should be the complete circle block
        assert any(r"\draw (0,0) circle (1);" in block for block in blocks)

    def test_extract_tikz_with_typos_in_environment_name(self, temp_dir):
        """Test that typos in environment names are not matched."""
        content = r"""
        \begin{tikzpictur}  % Missing 'e'
        \draw (0,0) -- (1,1);
        \end{tikzpictur}
        
        \begin{tikzpicture}
        \draw (0,0) circle (1);
        \end{tikzpicture}
        """

        blocks = extractor.extract_tikz_from_text(content)

        # Should only find the correctly spelled block
        assert len(blocks) == 1
        assert r"\draw (0,0) circle (1);" in blocks[0]

    def test_extract_tikz_with_extra_whitespace(self, temp_dir):
        """Test extraction of TikZ blocks with unusual whitespace."""
        content = r"""
        \begin{tikzpicture}
        
        
        \draw (0,0) -- (1,1);
        
        
        \end{tikzpicture}
        """

        blocks = extractor.extract_tikz_from_text(content)

        assert len(blocks) == 1
        # Should preserve whitespace within the block
        assert "\n        \n        \n" in blocks[0] or "\n\n" in blocks[0]


class TestLargeFilesAndDirectories:
    """Test handling of large files and directory structures."""

    def test_extract_from_large_directory_structure(self, temp_dir):
        """Test extraction from a large nested directory structure."""
        # Create a deep directory structure
        current_dir = temp_dir
        for i in range(10):  # 10 levels deep
            current_dir = current_dir / f"level_{i}"
            current_dir.mkdir()

            # Add a file at each level
            (current_dir / f"file_{i}.tex").write_text(
                f"\\begin{{tikzpicture}}\\node {{Level {i}}}; \\end{{tikzpicture}}",
                encoding="utf-8",
            )

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        # Should find all 10 TikZ blocks
        assert len(metadata) == 10

        # Verify each level is represented
        for i in range(10):
            assert any(f"Level {i}" in meta["content"] for meta in metadata)

    def test_extract_from_file_with_many_tikz_blocks(self, temp_dir):
        """Test extraction from a file with many TikZ blocks."""
        # Create a file with 50 TikZ blocks
        content_parts = []
        for i in range(50):
            content_parts.append(
                f"\\begin{{tikzpicture}}\\node {{Block {i}}}; \\end{{tikzpicture}}"
            )

        content = "\n\n".join(content_parts)
        (temp_dir / "many_blocks.tex").write_text(content, encoding="utf-8")

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        # Should find all 50 blocks
        assert len(metadata) == 50

        # Verify indices are correct
        indices = [meta["index"] for meta in metadata]
        assert indices == list(range(1, 51))

        # Verify each block is unique
        contents = [meta["content"] for meta in metadata]
        assert len(set(contents)) == 50


class TestSpecialCharactersAndUnicode:
    """Test handling of special characters and Unicode content."""

    def test_extract_tikz_with_unicode_characters(self, temp_dir):
        """Test extraction of TikZ blocks containing Unicode characters."""
        content = r"""
        \begin{tikzpicture}
        \node at (0,0) {Héllo Wörld};
        \node at (1,1) {数学};
        \node at (2,2) {Математика};
        \end{tikzpicture}
        """

        (temp_dir / "unicode.tex").write_text(content, encoding="utf-8")

        out_dir = temp_dir / "output"
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])

        assert len(metadata) == 1
        assert "Héllo Wörld" in metadata[0]["content"]
        assert "数学" in metadata[0]["content"]
        assert "Математика" in metadata[0]["content"]

        # Verify the output file contains the Unicode characters
        out_path = Path(metadata[0]["out_path"])
        file_content = out_path.read_text(encoding="utf-8")
        assert "Héllo Wörld" in file_content

    def test_sanitize_name_with_special_characters(self):
        """Test path sanitization with special characters."""
        # Test various special characters that might appear in paths
        test_paths = [
            Path("normal/path.tex"),
            Path("path with spaces/file.tex"),
            Path("path-with-dashes/file.tex"),
            Path("path_with_underscores/file.tex"),
            Path("path.with.dots/file.tex"),
        ]

        for path in test_paths:
            result = extractor.sanitize_name(path)
            # Should not contain path separators
            assert "/" not in result
            assert "\\" not in result
            # Should contain double underscores as replacements
            if "/" in str(path) or "\\" in str(path):
                assert "__" in result
