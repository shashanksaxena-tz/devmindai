"""Tests for MetadataManager."""

from pathlib import Path
import pytest
import json
from src.agents.project_documenter.metadata_manager import MetadataManager, FolderMetadata


def test_metadata_manager_tracks_folder_hashes(tmp_path):
    """Test that MetadataManager stores and retrieves folder hashes."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    manager = MetadataManager()
    manager.initialize(project_path)

    # Update folder metadata
    folder_path = project_path / "src"
    manager.update_folder(folder_path, file_count=1)

    # Verify metadata is stored
    metadata = manager.get_folder_metadata(folder_path)
    assert metadata is not None
    assert metadata.file_count == 1
    assert metadata.content_hash != ""


def test_metadata_manager_detects_changes(tmp_path):
    """Test that MetadataManager detects when folder content changes."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    manager = MetadataManager()
    manager.initialize(project_path)

    folder_path = project_path / "src"
    manager.update_folder(folder_path, file_count=1)

    # Should not detect change initially
    assert manager.has_folder_changed(folder_path) is False

    # Modify file
    (project_path / "src" / "main.py").write_text("print('world')")

    # Should detect change
    assert manager.has_folder_changed(folder_path) is True


def test_metadata_manager_creates_devmind_directory(tmp_path):
    """Test that .devmind directory is created."""
    project_path = tmp_path / "project"
    project_path.mkdir()

    manager = MetadataManager()
    manager.initialize(project_path)

    assert (project_path / ".devmind").exists()
    assert (project_path / ".devmind").is_dir()


def test_metadata_manager_persists_to_file(tmp_path):
    """Test that metadata is saved to disk."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("print('hello')")

    manager = MetadataManager()
    manager.initialize(project_path)
    manager.update_folder(project_path / "src", file_count=1)

    # Check file was created
    metadata_file = project_path / ".devmind" / "doc-metadata.json"
    assert metadata_file.exists()

    # Load and verify content
    with open(metadata_file) as f:
        data = json.load(f)

    assert "folders" in data
    assert "src" in data["folders"]
    assert data["folders"]["src"]["file_count"] == 1


def test_metadata_manager_loads_existing(tmp_path):
    """Test that existing metadata is loaded."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".devmind").mkdir()

    # Create existing metadata
    metadata = {
        "version": "1.0",
        "last_full_run": "2025-01-01T00:00:00Z",
        "project_root": str(project_path),
        "folders": {
            "src": {
                "last_generated": "2025-01-01T00:00:00Z",
                "content_hash": "abc123",
                "file_count": 5,
                "files": {"main.py": "hash1"},
            }
        },
    }
    
    with open(project_path / ".devmind" / "doc-metadata.json", "w") as f:
        json.dump(metadata, f)

    # Load
    manager = MetadataManager()
    manager.initialize(project_path)

    assert manager.get_last_full_run() == "2025-01-01T00:00:00Z"


def test_metadata_manager_mark_full_run(tmp_path):
    """Test marking a full run."""
    project_path = tmp_path / "project"
    project_path.mkdir()

    manager = MetadataManager()
    manager.initialize(project_path)
    
    assert manager.get_last_full_run() is None
    
    manager.mark_full_run()
    
    assert manager.get_last_full_run() is not None
    assert "T" in manager.get_last_full_run()  # ISO format


def test_metadata_manager_new_folder_is_changed(tmp_path):
    """Test that new folders are reported as changed."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("code")

    manager = MetadataManager()
    manager.initialize(project_path)

    # New folder should be reported as changed
    assert manager.has_folder_changed(project_path / "src") is True


def test_metadata_manager_clear_metadata(tmp_path):
    """Test clearing metadata."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("code")

    manager = MetadataManager()
    manager.initialize(project_path)
    manager.update_folder(project_path / "src", file_count=1)
    manager.mark_full_run()
    
    # Clear
    manager.clear_metadata()
    
    assert manager.get_last_full_run() is None
    assert len(manager.get_all_tracked_folders()) == 0


def test_metadata_manager_get_all_tracked_folders(tmp_path):
    """Test getting all tracked folders."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "src").mkdir()
    (project_path / "src" / "main.py").write_text("code")
    (project_path / "tests").mkdir()
    (project_path / "tests" / "test_main.py").write_text("test")

    manager = MetadataManager()
    manager.initialize(project_path)
    manager.update_folder(project_path / "src", file_count=1)
    manager.update_folder(project_path / "tests", file_count=1)
    
    folders = manager.get_all_tracked_folders()
    assert "src" in folders
    assert "tests" in folders
    assert len(folders) == 2


def test_folder_metadata_dataclass():
    """Test FolderMetadata dataclass."""
    metadata = FolderMetadata(
        last_generated="2025-01-01T00:00:00Z",
        content_hash="abc123",
        file_count=5,
        files={"main.py": "hash1"},
    )
    
    assert metadata.last_generated == "2025-01-01T00:00:00Z"
    assert metadata.content_hash == "abc123"
    assert metadata.file_count == 5
    assert metadata.files == {"main.py": "hash1"}


def test_metadata_manager_handles_corrupted_json(tmp_path):
    """Test handling of corrupted metadata file."""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / ".devmind").mkdir()

    # Create corrupted file
    with open(project_path / ".devmind" / "doc-metadata.json", "w") as f:
        f.write("{ invalid json")

    manager = MetadataManager()
    manager.initialize(project_path)  # Should not raise

    # Should start fresh
    assert manager.get_last_full_run() is None
