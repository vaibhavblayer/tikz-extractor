"""Unit tests for core extraction functions in tikz_extractor.extractor module."""

from pathlib import Path

import pytest

from tikz_extractor import extractor


class TestFindFiles:
    """Test the find_files function."""

    def test_find_files_single_extension(self, test_file_structure):
        """Test finding files with a single extension."""
        files = extractor.find_files(test_file_structure, [".tex"])
        tex_files = [f for f in files if f.suffix == ".tex"]

        assert len(tex_files) >= 5  # We have several .tex files
        assert any("single_tikz.tex" in str(f) for f in tex_files)
        assert any("multiple_tikz.tex" in str(f) for f in tex_files)
        assert any("no_tikz.tex" in str(f) for f in tex_files)

    def test_find_files_multiple_extensions(self, test_file_structure):
        """Test finding files with multiple extensions."""
        files = extractor.find_files(test_file_structure, [".tex", ".md", ".py"])

        # Should find .tex, .md, and .py files
        tex_files = [f for f in files if f.suffix == ".tex"]
        md_files = [f for f in files if f.suffix == ".md"]
        py_files = [f for f in files if f.suffix == ".py"]

        assert len(tex_files) >= 5
        assert len(md_files) >= 2
        assert len(py_files) >= 1

    def test_find_files_with_dots_in_extensions(self, test_file_structure):
        """Test that extensions work with or without leading dots."""
        files_with_dots = extractor.find_files(test_file_structure, [".tex", ".md"])
        files_without_dots = extractor.find_files(test_file_structure, ["tex", "md"])

        # Should find the same files regardless of dot prefix
        assert len(files_with_dots) == len(files_without_dots)
        assert set(files_with_dots) == set(files_without_dots)

    def test_find_files_recursive_search(self, test_file_structure):
        """Test that search is recursive and finds nested files."""
        files = extractor.find_files(test_file_structure, [".tex", ".md"])

        # Should find files in nested directories
        nested_files = [f for f in files if "nested" in str(f)]
        assert len(nested_files) >= 2
        assert any("deep_tikz.tex" in str(f) for f in nested_files)
        assert any("mid_level.md" in str(f) for f in nested_files)

    def test_find_files_empty_directory(self, temp_dir):
        """Test finding files in an empty directory."""
        empty_subdir = temp_dir / "empty"
        empty_subdir.mkdir()

        files = extractor.find_files(empty_subdir, [".tex"])
        assert len(files) == 0

    def test_find_files_no_matching_extensions(self, test_file_structure):
        """Test finding files when no files match the extensions."""
        files = extractor.find_files(test_file_structure, [".xyz", ".abc"])
        assert len(files) == 0


class TestSanitizeName:
    """Test the sanitize_name function."""

    def test_sanitize_simple_path(self):
        """Test sanitizing a simple file path."""
        path = Path("file.tex")
        result = extractor.sanitize_name(path)
        assert result == "file.tex"

    def test_sanitize_nested_path_forward_slash(self):
        """Test sanitizing a nested path with forward slashes."""
        path = Path("src/diagrams/flow.tex")
        result = extractor.sanitize_name(path)
        assert result == "src__diagrams__flow.tex"

    def test_sanitize_nested_path_backslash(self):
        """Test sanitizing a path with backslashes (Windows-style)."""
        # Simulate a Windows-style path string
        path_str = "src\\diagrams\\flow.tex"
        result = extractor.sanitize_name(Path(path_str))
        # Should replace both forward and back slashes
        assert "__" in result
        assert "\\" not in result
        assert "/" not in result

    def test_sanitize_deep_nested_path(self):
        """Test sanitizing a deeply nested path."""
        path = Path("very/deep/nested/directory/structure/file.tex")
        result = extractor.sanitize_name(path)
        expected = "very__deep__nested__directory__structure__file.tex"
        assert result == expected

    def test_sanitize_path_with_special_chars(self):
        """Test sanitizing paths that might have special characters."""
        path = Path("docs/README.md")
        result = extractor.sanitize_name(path)
        assert result == "docs__README.md"


class TestExtractTikzFromText:
    """Test the extract_tikz_from_text function."""

    def test_extract_single_tikz_block(self, sample_tikz_content):
        """Test extracting a single TikZ block."""
        text = f"Some text before {sample_tikz_content['simple']} some text after"
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 1
        assert blocks[0] == sample_tikz_content["simple"]

    def test_extract_multiple_tikz_blocks(self, sample_tikz_content):
        """Test extracting multiple TikZ blocks from the same text."""
        text = f"""
        First block: {sample_tikz_content['simple']}
        Some text in between.
        Second block: {sample_tikz_content['complex']}
        """
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 2
        assert sample_tikz_content["simple"] in blocks
        assert sample_tikz_content["complex"] in blocks

    def test_extract_multiline_tikz_block(self, sample_tikz_content):
        """Test extracting multiline TikZ blocks."""
        text = f"Before\n{sample_tikz_content['multiline']}\nAfter"
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 1
        assert blocks[0] == sample_tikz_content["multiline"]

    def test_extract_tikz_with_options(self, sample_tikz_content):
        """Test extracting TikZ blocks with options."""
        blocks = extractor.extract_tikz_from_text(sample_tikz_content["with_options"])

        assert len(blocks) == 1
        assert "scale=0.5" in blocks[0]
        assert "transform shape" in blocks[0]

    def test_extract_no_tikz_blocks(self):
        """Test extracting from text with no TikZ blocks."""
        text = "This is just regular text with no TikZ content."
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 0

    def test_extract_malformed_tikz(self):
        """Test extracting from text with malformed TikZ (missing end tag)."""
        text = r"\begin{tikzpicture}\draw (0,0) -- (1,1);"  # Missing \end{tikzpicture}
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 0  # Should not match incomplete blocks

    def test_extract_nested_environments(self):
        """Test extracting TikZ blocks with nested environments."""
        text = r"""
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \begin{scope}[shift={(2,0)}]
        \draw (0,0) circle (0.5);
        \end{scope}
        \end{tikzpicture}
        """
        blocks = extractor.extract_tikz_from_text(text)

        assert len(blocks) == 1
        assert r"\begin{scope}" in blocks[0]
        assert r"\end{scope}" in blocks[0]


class TestWriteExtractedBlocks:
    """Test the write_extracted_blocks function."""

    def test_write_single_block(self, temp_dir, sample_tikz_content):
        """Test writing a single TikZ block to file."""
        blocks = [sample_tikz_content["simple"]]
        src_path = Path("test.tex")
        out_dir = temp_dir / "output"

        metadata = extractor.write_extracted_blocks(blocks, src_path, out_dir)

        assert len(metadata) == 1
        assert metadata[0]["source"] == str(src_path)
        assert metadata[0]["index"] == 1
        assert metadata[0]["content"] == sample_tikz_content["simple"]

        # Check that file was actually written
        out_path = Path(metadata[0]["out_path"])
        assert out_path.exists()
        assert out_path.read_text(encoding="utf-8") == sample_tikz_content["simple"]

    def test_write_multiple_blocks(self, temp_dir, sample_tikz_content):
        """Test writing multiple TikZ blocks to separate files."""
        blocks = [sample_tikz_content["simple"], sample_tikz_content["complex"]]
        src_path = Path("multi.tex")
        out_dir = temp_dir / "output"

        metadata = extractor.write_extracted_blocks(blocks, src_path, out_dir)

        assert len(metadata) == 2
        assert metadata[0]["index"] == 1
        assert metadata[1]["index"] == 2

        # Check that both files were written
        for meta in metadata:
            out_path = Path(meta["out_path"])
            assert out_path.exists()
            assert out_path.read_text(encoding="utf-8") == meta["content"]

    def test_write_creates_output_directory(self, temp_dir, sample_tikz_content):
        """Test that output directory is created if it doesn't exist."""
        blocks = [sample_tikz_content["simple"]]
        src_path = Path("test.tex")
        out_dir = temp_dir / "new_output_dir"

        assert not out_dir.exists()

        metadata = extractor.write_extracted_blocks(blocks, src_path, out_dir)

        assert out_dir.exists()
        assert out_dir.is_dir()
        assert len(metadata) == 1

    def test_write_filename_generation(self, temp_dir, sample_tikz_content):
        """Test that filenames are generated correctly."""
        blocks = [sample_tikz_content["simple"], sample_tikz_content["complex"]]
        src_path = Path("src/nested/file.tex")
        out_dir = temp_dir / "output"

        metadata = extractor.write_extracted_blocks(blocks, src_path, out_dir)

        # Check filename format
        expected_base = "src__nested__file.tex"
        assert f"{expected_base}__tikz1.tex" in metadata[0]["out_path"]
        assert f"{expected_base}__tikz2.tex" in metadata[1]["out_path"]

    def test_write_empty_blocks_list(self, temp_dir):
        """Test writing an empty list of blocks."""
        blocks = []
        src_path = Path("empty.tex")
        out_dir = temp_dir / "output"

        metadata = extractor.write_extracted_blocks(blocks, src_path, out_dir)

        assert len(metadata) == 0
        assert out_dir.exists()  # Directory should still be created


class TestBuildAiContext:
    """Test the build_ai_context function."""

    def test_build_ai_context_single_block(self, temp_dir, sample_metadata):
        """Test building AI context file with a single block."""
        ai_file = temp_dir / "ai_context.txt"
        single_metadata = [sample_metadata[0]]

        extractor.build_ai_context(single_metadata, ai_file)

        assert ai_file.exists()
        content = ai_file.read_text(encoding="utf-8")

        # Check format
        assert "### Source:" in content
        assert "### Snippet:" in content
        assert sample_metadata[0]["content"] in content
        assert "---" not in content  # No separator for single block

    def test_build_ai_context_multiple_blocks(self, temp_dir, sample_metadata):
        """Test building AI context file with multiple blocks."""
        ai_file = temp_dir / "ai_context.txt"

        extractor.build_ai_context(sample_metadata, ai_file)

        assert ai_file.exists()
        content = ai_file.read_text(encoding="utf-8")

        # Check that both blocks are present
        for meta in sample_metadata:
            assert meta["source"] in content
            assert meta["content"] in content

        # Check separator between blocks
        assert "---" in content
        separator_count = content.count("---")
        assert (
            separator_count == len(sample_metadata) - 1
        )  # n-1 separators for n blocks

    def test_build_ai_context_format(self, temp_dir, sample_metadata):
        """Test the specific format of the AI context file."""
        ai_file = temp_dir / "ai_context.txt"

        extractor.build_ai_context(sample_metadata, ai_file)

        content = ai_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Check header format for first block
        assert lines[0].startswith("### Source:")
        assert lines[1].startswith("### Snippet:")
        assert sample_metadata[0]["content"] in content

    def test_build_ai_context_empty_metadata(self, temp_dir):
        """Test building AI context with empty metadata list."""
        ai_file = temp_dir / "ai_context.txt"

        extractor.build_ai_context([], ai_file)

        assert ai_file.exists()
        content = ai_file.read_text(encoding="utf-8")
        assert content == ""  # Should be empty file

    def test_build_ai_context_overwrites_existing(self, temp_dir, sample_metadata):
        """Test that AI context file overwrites existing content."""
        ai_file = temp_dir / "ai_context.txt"
        ai_file.write_text("Old content", encoding="utf-8")

        extractor.build_ai_context(sample_metadata, ai_file)

        content = ai_file.read_text(encoding="utf-8")
        assert "Old content" not in content
        assert sample_metadata[0]["content"] in content
