"""Integration tests for complete TikZ extraction workflow."""

from pathlib import Path

import pytest

from tikz_extractor import extractor


class TestExtractFromDirectory:
    """Test the complete extract_from_directory workflow."""

    def test_extract_from_directory_basic(self, test_file_structure):
        """Test basic directory extraction workflow."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md", ".py"]
        )

        # Should find TikZ blocks from multiple files
        assert len(metadata) > 0

        # Check that output directory was created
        assert out_dir.exists()
        assert out_dir.is_dir()

        # Verify metadata structure
        for meta in metadata:
            assert "source" in meta
            assert "out_path" in meta
            assert "index" in meta
            assert "content" in meta
            assert meta["content"].startswith(r"\begin{tikzpicture}")
            assert meta["content"].endswith(r"\end{tikzpicture}")

    def test_extract_from_directory_file_creation(self, test_file_structure):
        """Test that extracted files are actually created."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md", ".py"]
        )

        # Verify that all referenced output files exist
        for meta in metadata:
            out_path = Path(meta["out_path"])
            assert out_path.exists()
            assert out_path.is_file()

            # Verify file content matches metadata
            file_content = out_path.read_text(encoding="utf-8")
            assert file_content == meta["content"]

    def test_extract_from_directory_multiple_blocks_per_file(self, test_file_structure):
        """Test extraction from files with multiple TikZ blocks."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex"]
        )

        # Find metadata for the multiple_tikz.tex file
        multiple_tikz_metadata = [
            meta for meta in metadata if "multiple_tikz.tex" in meta["source"]
        ]

        # Should have found 2 blocks from multiple_tikz.tex
        assert len(multiple_tikz_metadata) == 2
        assert multiple_tikz_metadata[0]["index"] == 1
        assert multiple_tikz_metadata[1]["index"] == 2

        # Verify different content
        assert (
            multiple_tikz_metadata[0]["content"] != multiple_tikz_metadata[1]["content"]
        )

    def test_extract_from_directory_nested_files(self, test_file_structure):
        """Test extraction from nested directory structure."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md"]
        )

        # Should find blocks from nested files
        nested_sources = [
            meta["source"] for meta in metadata if "nested" in meta["source"]
        ]

        assert len(nested_sources) >= 2
        assert any("deep_tikz.tex" in source for source in nested_sources)
        assert any("mid_level.md" in source for source in nested_sources)

    def test_extract_from_directory_specific_extensions(self, test_file_structure):
        """Test extraction with specific file extensions only."""
        out_dir = test_file_structure / "extracted"

        # Extract only from .tex files
        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex"]
        )

        # All sources should be .tex files
        for meta in metadata:
            assert meta["source"].endswith(".tex")

        # Should not find any .md or .py sources
        md_sources = [meta for meta in metadata if meta["source"].endswith(".md")]
        py_sources = [meta for meta in metadata if meta["source"].endswith(".py")]

        assert len(md_sources) == 0
        assert len(py_sources) == 0

    def test_extract_from_directory_no_tikz_files(self, temp_dir):
        """Test extraction from directory with no TikZ content."""
        # Create files without TikZ content
        (temp_dir / "no_tikz1.tex").write_text("Just regular LaTeX", encoding="utf-8")
        (temp_dir / "no_tikz2.md").write_text("# Just markdown", encoding="utf-8")

        out_dir = temp_dir / "extracted"

        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex", ".md"])

        assert len(metadata) == 0
        # Output directory should still be created by write_extracted_blocks
        # but it will be empty

    def test_extract_from_directory_empty_directory(self, temp_dir):
        """Test extraction from empty directory."""
        empty_dir = temp_dir / "empty"
        empty_dir.mkdir()
        out_dir = temp_dir / "extracted"

        metadata = extractor.extract_from_directory(empty_dir, out_dir, [".tex", ".md"])

        assert len(metadata) == 0

    def test_extract_from_directory_error_handling(
        self, test_file_structure, binary_file
    ):
        """Test that extraction continues despite file reading errors."""
        out_dir = test_file_structure / "extracted"

        # The binary file should cause encoding errors but extraction should continue
        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md", ".py"]
        )

        # Should still find TikZ blocks from readable files
        assert len(metadata) > 0

        # Verify that some files were processed successfully
        sources = [meta["source"] for meta in metadata]
        assert any("single_tikz.tex" in source for source in sources)


class TestCompleteWorkflow:
    """Test the complete workflow from directory scanning to AI context generation."""

    def test_complete_workflow_end_to_end(self, test_file_structure):
        """Test complete end-to-end workflow."""
        out_dir = test_file_structure / "extracted"
        ai_file = test_file_structure / "ai_context.txt"

        # Step 1: Extract from directory
        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md", ".py"]
        )

        assert len(metadata) > 0

        # Step 2: Build AI context
        extractor.build_ai_context(metadata, ai_file)

        # Verify AI context file was created
        assert ai_file.exists()
        ai_content = ai_file.read_text(encoding="utf-8")

        # Verify AI context contains all extracted blocks
        for meta in metadata:
            assert meta["content"] in ai_content
            assert meta["source"] in ai_content

        # Verify format
        assert "### Source:" in ai_content
        assert "### Snippet:" in ai_content

        if len(metadata) > 1:
            assert "---" in ai_content  # Separators between blocks

    def test_workflow_metadata_accuracy(self, test_file_structure):
        """Test that metadata accurately reflects the extraction results."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex"]
        )

        # Verify metadata accuracy
        for meta in metadata:
            # Check source file exists
            source_path = Path(meta["source"])
            assert source_path.exists()

            # Check output file exists and has correct content
            out_path = Path(meta["out_path"])
            assert out_path.exists()

            file_content = out_path.read_text(encoding="utf-8")
            assert file_content == meta["content"]

            # Check filename format
            expected_filename = (
                f"{extractor.sanitize_name(source_path)}__tikz{meta['index']}.tex"
            )
            assert out_path.name == expected_filename

    def test_workflow_file_output_correctness(self, test_file_structure):
        """Test that output files contain correct TikZ content."""
        out_dir = test_file_structure / "extracted"

        metadata = extractor.extract_from_directory(
            test_file_structure, out_dir, [".tex", ".md", ".py"]
        )

        # Verify each output file
        for meta in metadata:
            out_path = Path(meta["out_path"])
            content = out_path.read_text(encoding="utf-8")

            # Should be valid TikZ block
            assert content.startswith(r"\begin{tikzpicture}")
            assert content.endswith(r"\end{tikzpicture}")

            # Should match metadata content exactly
            assert content == meta["content"]

    def test_workflow_with_different_source_structures(self, temp_dir):
        """Test workflow with different directory structures."""
        # Create a complex directory structure
        (temp_dir / "level1").mkdir()
        (temp_dir / "level1" / "level2").mkdir()
        (temp_dir / "level1" / "level2" / "level3").mkdir()

        # Add TikZ files at different levels
        (temp_dir / "root.tex").write_text(
            r"""
        \begin{tikzpicture}
        \draw (0,0) -- (1,1);
        \end{tikzpicture}
        """,
            encoding="utf-8",
        )

        (temp_dir / "level1" / "mid.tex").write_text(
            r"""
        \begin{tikzpicture}
        \node {Middle};
        \end{tikzpicture}
        """,
            encoding="utf-8",
        )

        (temp_dir / "level1" / "level2" / "level3" / "deep.tex").write_text(
            r"""
        \begin{tikzpicture}
        \draw (0,0) circle (1);
        \end{tikzpicture}
        """,
            encoding="utf-8",
        )

        out_dir = temp_dir / "extracted"
        ai_file = temp_dir / "ai_context.txt"

        # Run complete workflow
        metadata = extractor.extract_from_directory(temp_dir, out_dir, [".tex"])
        extractor.build_ai_context(metadata, ai_file)

        # Should find all 3 TikZ blocks
        assert len(metadata) == 3

        # Verify all files were created
        for meta in metadata:
            assert Path(meta["out_path"]).exists()

        # Verify AI context includes all blocks
        ai_content = ai_file.read_text(encoding="utf-8")
        assert "root.tex" in ai_content
        assert "mid.tex" in ai_content
        assert "deep.tex" in ai_content
