"""Backup and restore shell configuration files"""

import shutil
import os
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple, Callable
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
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    self.manifest = json.load(f)
            except:
                self.manifest = {"backups": []}
        else:
            self.manifest = {"backups": []}

    def _save_manifest(self):
        """Save backup manifest"""
        try:
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
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


def atomic_write_shell_config(file_path: Path, content: str,
                               validate_func: Optional[Callable[[str], Tuple[bool, str]]] = None,
                               backup_manager: Optional[BackupManager] = None) -> Tuple[bool, str]:
    """
    Atomically write to a shell config file with validation (v1.1.5 Security Enhancement)

    This function prevents corrupted shell configs by:
    1. Creating a backup first
    2. Writing to a temporary file
    3. Validating the content (optional)
    4. Atomically renaming to target (prevents partial writes)
    5. Auto-recovery on failure

    Args:
        file_path: Path to shell config file (.bashrc, .zshrc, etc.)
        content: New content to write
        validate_func: Optional validation function (content) -> (is_valid, error_message)
        backup_manager: Optional BackupManager instance for backups

    Returns:
        Tuple of (success, message)

    Example:
        >>> def validate_bashrc(content: str) -> Tuple[bool, str]:
        ...     if 'CCMD_HOME' not in content:
        ...         return False, "Missing CCMD_HOME"
        ...     return True, ""
        >>> success, msg = atomic_write_shell_config(Path("~/.bashrc"), content, validate_bashrc)
    """
    if backup_manager is None:
        backup_manager = BackupManager()

    try:
        # Step 1: Create backup FIRST (safety net)
        if file_path.exists():
            success, backup_result = backup_manager.create_backup(
                file_path,
                description="Pre-atomic-write backup"
            )
            if not success:
                return False, f"Backup failed: {backup_result}"
            backup_path = Path(backup_result)
        else:
            backup_path = None

        # Step 2: Validate content if validator provided
        if validate_func:
            is_valid, error_msg = validate_func(content)
            if not is_valid:
                return False, f"Validation failed: {error_msg}"

        # Step 3: Write to temporary file in same directory (ensures same filesystem)
        # Using same directory ensures os.rename() is atomic
        temp_fd, temp_path_str = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )

        try:
            temp_path = Path(temp_path_str)

            # Write content to temp file
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(content)

            # Step 4: Set same permissions as original (if exists)
            if file_path.exists():
                original_stat = file_path.stat()
                os.chmod(temp_path, original_stat.st_mode)

            # Step 5: Atomic rename (this is the critical security improvement)
            # os.replace() is atomic on both Unix and Windows
            os.replace(temp_path, file_path)

            return True, f"Successfully wrote {file_path}"

        except Exception as write_error:
            # Clean up temp file on failure
            if Path(temp_path_str).exists():
                try:
                    os.unlink(temp_path_str)
                except:
                    pass
            raise write_error

    except Exception as e:
        # Step 6: Auto-recovery - restore backup on failure
        if backup_path and backup_path.exists():
            try:
                backup_manager.restore_backup(backup_path=backup_path)
                return False, f"Write failed, backup restored: {e}"
            except Exception as restore_error:
                return False, f"Write failed AND restore failed: {e} | {restore_error}"
        else:
            return False, f"Write failed: {e}"


def validate_shell_syntax(content: str, shell_type: str = 'bash') -> Tuple[bool, str]:
    """
    Validate shell config syntax (v1.1.5 Security Enhancement)

    Args:
        content: Shell config content to validate
        shell_type: Shell type (bash, zsh, fish, powershell)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Write to temp file for syntax checking
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            temp_file = f.name
            f.write(content)

        try:
            if shell_type in ('bash', 'zsh'):
                # Use shell's -n flag to check syntax without executing
                shell_cmd = 'bash' if shell_type == 'bash' else 'zsh'
                result = subprocess.run(
                    [shell_cmd, '-n', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, f"Syntax error: {result.stderr}"

            elif shell_type == 'fish':
                # Fish uses --no-execute
                result = subprocess.run(
                    ['fish', '--no-execute', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return False, f"Syntax error: {result.stderr}"

            elif shell_type == 'powershell':
                # PowerShell uses -File with -NoExecute (syntax check)
                result = subprocess.run(
                    ['powershell', '-NoProfile', '-File', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                # PowerShell doesn't have a pure syntax check, so we just ensure no crashes
                if result.returncode not in (0, 1):
                    return False, f"Syntax error: {result.stderr}"

            return True, ""

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass

    except Exception as e:
        return False, f"Validation failed: {e}"


class RollbackManager:
    """High-level rollback operations"""

    def __init__(self, backup_manager: Optional[BackupManager] = None):
        """
        Initialize rollback manager

        Args:
            backup_manager: BackupManager instance
        """
        self.backup_manager = backup_manager or BackupManager()

    def safe_file_edit(self, file_path: Path, edit_func, description: str = "",
                      use_atomic_write: bool = True, validate_func: Optional[Callable[[str], Tuple[bool, str]]] = None):
        """
        Safely edit a file with automatic backup (v1.1.5: Now uses atomic writes by default)

        Args:
            file_path: Path to file to edit
            edit_func: Function that performs the edit (takes file content, returns new content)
            description: Description of the edit
            use_atomic_write: If True, use atomic write (default). Set False for non-critical files.
            validate_func: Optional validation function for atomic writes

        Returns:
            Tuple of (success, message)
        """
        try:
            # Read current content
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = ""

            # Apply edit
            new_content = edit_func(content)

            # Write new content
            file_path.parent.mkdir(parents=True, exist_ok=True)

            if use_atomic_write:
                # Use atomic write for shell configs (v1.1.5 security enhancement)
                success, message = atomic_write_shell_config(
                    file_path,
                    new_content,
                    validate_func=validate_func,
                    backup_manager=self.backup_manager
                )
                return success, message
            else:
                # Legacy direct write (for non-critical files)
                # Create backup first
                if file_path.exists():
                    success, result = self.backup_manager.create_backup(file_path, description)
                    if not success:
                        return False, f"Backup failed: {result}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return True, "File edited successfully"

        except Exception as e:
            # Try to restore backup on failure
            if file_path.exists():
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
