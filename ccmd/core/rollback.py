"""Backup and restore shell configuration files"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
import json


class BackupManager:
    """Manage backups of shell configuration files"""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory to store backups. If None, uses ~/.ccmd/backups
        """
        if backup_dir is None:
            self.backup_dir = Path.home() / ".ccmd" / "backups"
        else:
            self.backup_dir = Path(backup_dir)

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.backup_dir / "manifest.json"
        self._load_manifest()

    def _load_manifest(self):
        """Load backup manifest"""
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, 'r') as f:
                    self.manifest = json.load(f)
            except:
                self.manifest = {"backups": []}
        else:
            self.manifest = {"backups": []}

    def _save_manifest(self):
        """Save backup manifest"""
        try:
            with open(self.manifest_file, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save manifest: {e}")

    def create_backup(self, file_path: Path, description: str = "") -> Tuple[bool, str]:
        """
        Create a backup of a file

        Args:
            file_path: Path to file to backup
            description: Optional description of the backup

        Returns:
            Tuple of (success, backup_path or error_message)
        """
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"

        try:
            # Create timestamp-based backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{file_path.name}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_filename

            # Copy file
            shutil.copy2(file_path, backup_path)

            # Add to manifest
            backup_entry = {
                "original_path": str(file_path),
                "backup_path": str(backup_path),
                "timestamp": timestamp,
                "description": description
            }
            self.manifest["backups"].append(backup_entry)
            self._save_manifest()

            return True, str(backup_path)

        except Exception as e:
            return False, f"Backup failed: {e}"

    def restore_backup(self, backup_path: Optional[Path] = None,
                      original_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Restore a backup file

        Args:
            backup_path: Path to backup file to restore
            original_path: Original file path. If None, uses manifest

        Returns:
            Tuple of (success, message)
        """
        # Find backup in manifest
        backup_entry = None

        if backup_path:
            backup_path_str = str(backup_path)
            for entry in self.manifest["backups"]:
                if entry["backup_path"] == backup_path_str:
                    backup_entry = entry
                    break
        elif original_path:
            # Find most recent backup for this file
            original_path_str = str(original_path)
            matching_backups = [
                entry for entry in self.manifest["backups"]
                if entry["original_path"] == original_path_str
            ]
            if matching_backups:
                backup_entry = matching_backups[-1]  # Most recent

        if not backup_entry:
            return False, "Backup not found in manifest"

        try:
            backup_file = Path(backup_entry["backup_path"])
            original_file = Path(backup_entry["original_path"])

            if not backup_file.exists():
                return False, f"Backup file not found: {backup_file}"

            # Create backup of current file before restoring
            if original_file.exists():
                current_backup = original_file.with_suffix(original_file.suffix + '.pre-restore')
                shutil.copy2(original_file, current_backup)

            # Restore backup
            shutil.copy2(backup_file, original_file)

            return True, f"Restored {original_file} from {backup_file}"

        except Exception as e:
            return False, f"Restore failed: {e}"

    def list_backups(self, file_path: Optional[Path] = None) -> List[dict]:
        """
        List available backups

        Args:
            file_path: If provided, only list backups for this file

        Returns:
            List of backup entries
        """
        if file_path:
            file_path_str = str(file_path)
            return [
                entry for entry in self.manifest["backups"]
                if entry["original_path"] == file_path_str
            ]
        return self.manifest["backups"]

    def get_latest_backup(self, file_path: Path) -> Optional[Path]:
        """
        Get the most recent backup for a file

        Args:
            file_path: Original file path

        Returns:
            Path to latest backup or None
        """
        backups = self.list_backups(file_path)
        if backups:
            latest = backups[-1]
            return Path(latest["backup_path"])
        return None

    def cleanup_old_backups(self, keep_count: int = 5):
        """
        Clean up old backups, keeping only the most recent ones

        Args:
            keep_count: Number of backups to keep per file
        """
        # Group backups by original file
        backups_by_file = {}
        for entry in self.manifest["backups"]:
            original = entry["original_path"]
            if original not in backups_by_file:
                backups_by_file[original] = []
            backups_by_file[original].append(entry)

        # Keep only recent backups
        new_manifest = {"backups": []}
        for original, backups in backups_by_file.items():
            # Sort by timestamp
            backups.sort(key=lambda x: x["timestamp"])

            # Keep recent ones
            to_keep = backups[-keep_count:]
            to_remove = backups[:-keep_count]

            # Delete old backup files
            for entry in to_remove:
                try:
                    backup_file = Path(entry["backup_path"])
                    if backup_file.exists():
                        backup_file.unlink()
                except:
                    pass

            # Add kept backups to new manifest
            new_manifest["backups"].extend(to_keep)

        # Update manifest
        self.manifest = new_manifest
        self._save_manifest()


class RollbackManager:
    """High-level rollback operations"""

    def __init__(self, backup_manager: Optional[BackupManager] = None):
        """
        Initialize rollback manager

        Args:
            backup_manager: BackupManager instance
        """
        self.backup_manager = backup_manager or BackupManager()

    def safe_file_edit(self, file_path: Path, edit_func, description: str = ""):
        """
        Safely edit a file with automatic backup

        Args:
            file_path: Path to file to edit
            edit_func: Function that performs the edit (takes file content, returns new content)
            description: Description of the edit

        Returns:
            Tuple of (success, message)
        """
        # Create backup first
        success, result = self.backup_manager.create_backup(file_path, description)
        if not success:
            return False, f"Backup failed: {result}"

        try:
            # Read current content
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
            else:
                content = ""

            # Apply edit
            new_content = edit_func(content)

            # Write new content
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(new_content)

            return True, "File edited successfully"

        except Exception as e:
            # Try to restore backup on failure
            self.backup_manager.restore_backup(original_path=file_path)
            return False, f"Edit failed: {e}"

    def restore_all(self) -> List[Tuple[str, bool, str]]:
        """
        Restore all backed up files to their most recent backup

        Returns:
            List of (file_path, success, message) tuples
        """
        results = []

        # Get unique original files
        backups = self.backup_manager.list_backups()
        original_files = set(entry["original_path"] for entry in backups)

        for file_path_str in original_files:
            file_path = Path(file_path_str)
            success, message = self.backup_manager.restore_backup(original_path=file_path)
            results.append((file_path_str, success, message))

        return results
