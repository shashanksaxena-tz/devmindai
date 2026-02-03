"""Metadata manager for tracking documentation generation state."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Optional, Any


@dataclass
class FolderMetadata:
    """Metadata for a documented folder."""

    last_generated: str  # ISO timestamp
    content_hash: str  # SHA256 hash of source files
    file_count: int
    files: Dict[str, str]  # filename -> hash


class MetadataManager:
    """Manages metadata for documentation generation tracking."""

    METADATA_DIR = ".devmind"
    METADATA_FILE = "doc-metadata.json"

    # Source code extensions to track
    SOURCE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".rb", ".php", ".kt", ".swift"}

    def __init__(self):
        """Initialize metadata manager."""
        self.project_root: Optional[Path] = None
        self.metadata_file: Optional[Path] = None
        self.metadata: Dict[str, Any] = {}

    def initialize(self, project_path: Path) -> None:
        """Initialize metadata for a project.

        Args:
            project_path: Root path of the project
        """
        self.project_root = project_path
        self.metadata_file = project_path / self.METADATA_DIR / self.METADATA_FILE

        # Create .devmind directory if it doesn't exist
        self.metadata_file.parent.mkdir(exist_ok=True)

        # Load existing metadata if present
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    self.metadata = json.load(f)
            except json.JSONDecodeError:
                # Corrupted file, start fresh
                self._init_fresh_metadata(project_path)
        else:
            self._init_fresh_metadata(project_path)

    def _init_fresh_metadata(self, project_path: Path) -> None:
        """Initialize fresh metadata structure."""
        self.metadata = {
            "version": "1.0",
            "last_full_run": None,
            "project_root": str(project_path),
            "folders": {},
        }

    def update_folder(self, folder_path: Path, file_count: int) -> None:
        """Update metadata for a folder after documentation generation.

        Args:
            folder_path: Path to the documented folder
            file_count: Number of source files in folder
        """
        if not self.project_root:
            raise RuntimeError("MetadataManager not initialized")

        relative_path = str(folder_path.relative_to(self.project_root))

        # Compute content hash
        content_hash, file_hashes = self._compute_folder_hash(folder_path)

        # Update metadata
        self.metadata["folders"][relative_path] = {
            "last_generated": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "content_hash": content_hash,
            "file_count": file_count,
            "files": file_hashes,
        }

        # Save to disk
        self._save()

    def get_folder_metadata(self, folder_path: Path) -> Optional[FolderMetadata]:
        """Get metadata for a folder.

        Args:
            folder_path: Path to the folder

        Returns:
            FolderMetadata if exists, None otherwise
        """
        if not self.project_root:
            return None

        try:
            relative_path = str(folder_path.relative_to(self.project_root))
        except ValueError:
            return None

        folder_data = self.metadata.get("folders", {}).get(relative_path)

        if folder_data:
            return FolderMetadata(
                last_generated=folder_data.get("last_generated", ""),
                content_hash=folder_data.get("content_hash", ""),
                file_count=folder_data.get("file_count", 0),
                files=folder_data.get("files", {}),
            )

        return None

    def has_folder_changed(self, folder_path: Path) -> bool:
        """Check if folder content has changed since last generation.

        Args:
            folder_path: Path to the folder

        Returns:
            True if folder has changed or is new, False otherwise
        """
        if not self.project_root:
            return True

        # Get stored metadata
        metadata = self.get_folder_metadata(folder_path)
        if not metadata:
            return True  # New folder

        # Compute current hash
        current_hash, _ = self._compute_folder_hash(folder_path)

        return current_hash != metadata.content_hash

    def _compute_folder_hash(self, folder_path: Path) -> tuple[str, Dict[str, str]]:
        """Compute SHA256 hash of all source files in folder.

        Args:
            folder_path: Path to the folder

        Returns:
            Tuple of (combined_hash, file_hashes)
        """
        file_hashes: Dict[str, str] = {}
        hash_list = []

        # Get all source files (only direct children, not recursive)
        try:
            source_files = sorted([
                f for f in folder_path.iterdir()
                if f.is_file() and f.suffix in self.SOURCE_EXTENSIONS
            ])
        except PermissionError:
            return "", {}

        for file_path in source_files:
            try:
                content = file_path.read_bytes()
                file_hash = hashlib.sha256(content).hexdigest()
                file_hashes[file_path.name] = file_hash
                hash_list.append(file_hash)
            except Exception:
                continue

        # Combine all file hashes
        combined = "".join(hash_list)
        combined_hash = hashlib.sha256(combined.encode()).hexdigest() if hash_list else ""

        return combined_hash, file_hashes

    def _save(self) -> None:
        """Save metadata to disk."""
        if not self.metadata_file:
            return

        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def mark_full_run(self) -> None:
        """Mark that a full documentation run has completed."""
        self.metadata["last_full_run"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        self._save()

    def get_last_full_run(self) -> Optional[str]:
        """Get timestamp of last full run.

        Returns:
            ISO timestamp string or None
        """
        return self.metadata.get("last_full_run")

    def clear_metadata(self) -> None:
        """Clear all stored metadata."""
        if self.project_root:
            self._init_fresh_metadata(self.project_root)
            self._save()

    def get_all_tracked_folders(self) -> list[str]:
        """Get list of all tracked folder paths.

        Returns:
            List of relative folder paths
        """
        return list(self.metadata.get("folders", {}).keys())
