"""Password authentication module for CCMD - v1.1.1
Provides master password protection for sensitive commands including SSH operations
CROSS-PLATFORM: Windows, Linux, macOS
"""

import os
import re
import stat
import sys
import time
import hashlib
import secrets
from pathlib import Path
from typing import Tuple, Optional
from getpass import getpass

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    # Will use PBKDF2 fallback - secure but slightly slower than bcrypt


# Configuration
AUTH_FILE = Path.home() / ".ccmd" / "ccmd.key"
AUTH_LOG = Path.home() / ".ccmd" / "ccmd_auth.log"
AUTH_CACHE_TTL = 300  # 5 minutes cache per process
MAX_AUTH_TRIES = 3

# In-memory cache for successful auth
_last_auth_ok = {"ts": 0}


def _set_secure_file_permissions(file_path: Path):
    """
    Set secure permissions on a file (CROSS-PLATFORM)

    Args:
        file_path: Path to file

    Platform-specific:
    - Unix/Linux/macOS: 0o600 (owner read/write only)
    - Windows: Best effort with available APIs
    """
    try:
        if sys.platform == 'win32':
            # Windows: Use stat flags
            os.chmod(file_path, stat.S_IREAD | stat.S_IWRITE)
        else:
            # Unix-like: Proper permissions
            os.chmod(file_path, 0o600)
    except Exception:
        pass  # Best effort - don't fail if permissions can't be set


def _hash_password_pbkdf2(password: str, salt: bytes = None) -> bytes:
    """
    Hash password using PBKDF2-HMAC-SHA256 (secure fallback when bcrypt unavailable)

    Args:
        password: Plain text password
        salt: Optional salt (generates new one if not provided)

    Returns:
        Combined salt + hash as bytes

    Format: salt (32 bytes) + hash (32 bytes) = 64 bytes total
    """
    if salt is None:
        salt = secrets.token_bytes(32)

    # PBKDF2 with 100,000 iterations (OWASP recommended minimum)
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,  # iterations
        dklen=32  # 32 bytes = 256 bits
    )

    # Return salt + hash combined
    return salt + hash_bytes


def _verify_password_pbkdf2(password: str, stored: bytes) -> bool:
    """
    Verify password against PBKDF2 hash

    Args:
        password: Plain text password to verify
        stored: Stored salt + hash (64 bytes)

    Returns:
        True if password matches
    """
    if len(stored) != 64:
        return False

    # Extract salt (first 32 bytes) and stored hash (last 32 bytes)
    salt = stored[:32]
    stored_hash = stored[32:]

    # Compute hash with same salt
    computed_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000,
        dklen=32
    )

    # Constant-time comparison to prevent timing attacks
    return secrets.compare_digest(computed_hash, stored_hash)


# Sensitive command patterns that require password (v1.1.2 - Expanded)
SENSITIVE_PATTERNS = [
    # SSH with embedded keys (multiple formats)
    re.compile(r"\bssh\b.*\s-i\s+\S+", re.I),
    re.compile(r"\bssh\b.*\s-oIdentityFile[=\s]+\S+", re.I),
    re.compile(r"\bscp\b.*\s-i\s+\S+", re.I),
    re.compile(r"\bsftp\b.*\s-i\s+\S+", re.I),
    re.compile(r"\brsync\b.*--rsh=.*ssh.*-i", re.I),
    re.compile(r"sshkey@\d{1,3}(?:\.\d{1,3}){3}"),  # sshkey@IP pattern

    # Password utilities (dangerous)
    re.compile(r"\bsshpass\b", re.I),

    # AWS/Cloud credentials (expanded)
    re.compile(r"\b(export|set)\s+AWS_SECRET", re.I),
    re.compile(r"\b(export|set)\s+AWS_ACCESS_KEY", re.I),
    re.compile(r"\b(export|set)\s+AZURE_", re.I),
    re.compile(r"\b(export|set)\s+GCP_", re.I),
    re.compile(r"\b(export|set)\s+GOOGLE_APPLICATION_CREDENTIALS", re.I),

    # Database credentials (expanded)
    re.compile(r"\bmysql\b.*(-p|--password)", re.I),
    re.compile(r"\bpsql\b.*password", re.I),
    re.compile(r"\b(export|set)\s+PGPASSWORD", re.I),
    re.compile(r"\b(export|set)\s+MYSQL_PWD", re.I),
    re.compile(r"\bmongo\b.*(-p|--password)", re.I),
    re.compile(r"\bredis-cli\b.*-a\s+", re.I),

    # Docker/Container credentials
    re.compile(r"\bdocker\s+login", re.I),
    re.compile(r"\bkubectl\b.*--token", re.I),
    re.compile(r"\bhelm\b.*--password", re.I),

    # Git with credentials
    re.compile(r"git\s+clone.*https?://[^@]+@", re.I),
    re.compile(r"git\s+.*(-c\s+)?credential\.", re.I),

    # API keys and tokens
    re.compile(r"(api[_-]?key|token)[=:\s]+['\"]?\w{20,}", re.I),
    re.compile(r"\b(export|set)\s+.*_(API_KEY|TOKEN|SECRET)", re.I),

    # Sudo/system commands
    re.compile(r"\bsudo\b", re.I),
    re.compile(r"\breboot\b", re.I),
    re.compile(r"\bshutdown\b", re.I),
    re.compile(r"\binit\s+[0-6]", re.I),  # init runlevel change

    # Generic password flags (catches many tools)
    re.compile(r"--password[=\s]+\S+", re.I),
    re.compile(r"-p\s*['\"].*['\"]", re.I),  # -p "password" pattern
]


def set_password(password: str) -> Tuple[bool, str]:
    """
    Set the master password for CCMD (v1.1.2 - Secure fallback)

    Uses bcrypt if available, otherwise falls back to PBKDF2-HMAC-SHA256.
    Both are cryptographically secure.

    Args:
        password: Master password

    Returns:
        Tuple of (success, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    try:
        # Hash password (bcrypt preferred, PBKDF2 fallback)
        if HAS_BCRYPT:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        else:
            # Secure fallback: PBKDF2 with 100k iterations
            hashed = _hash_password_pbkdf2(password)

        # Ensure directory exists
        AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Write hash to file
        with open(AUTH_FILE, 'wb') as f:
            f.write(hashed)

        # Set secure permissions (cross-platform)
        _set_secure_file_permissions(AUTH_FILE)

        hash_method = "bcrypt" if HAS_BCRYPT else "PBKDF2-HMAC-SHA256"
        return True, f"Master password set successfully (using {hash_method})"

    except Exception as e:
        return False, f"Failed to set password: {e}"


def verify_password_interactive(max_tries: int = MAX_AUTH_TRIES) -> bool:
    """
    Interactively verify master password with caching (v1.1.2 - Secure fallback)

    Auto-detects whether password was hashed with bcrypt or PBKDF2.
    SECURITY: Never bypasses authentication, even if bcrypt is missing.

    Args:
        max_tries: Maximum number of attempts

    Returns:
        True if authentication successful, False otherwise
    """
    # Check cache first
    if time.time() - _last_auth_ok["ts"] < AUTH_CACHE_TTL:
        return True

    # Check if password is set
    if not AUTH_FILE.exists():
        print("CCMD master password not set.")
        print("Run: python3 run.py --init")
        return False

    try:
        # Load stored hash
        hashed = AUTH_FILE.read_bytes()

        # Detect hash format: bcrypt starts with $2b$, PBKDF2 is 64 bytes
        is_bcrypt = hashed.startswith(b'$2b$') or hashed.startswith(b'$2a$')
        is_pbkdf2 = len(hashed) == 64

        if is_bcrypt and not HAS_BCRYPT:
            print("ERROR: Password was set with bcrypt, but bcrypt is not installed.")
            print("Install with: pip install bcrypt")
            return False

        # Verify password with retries
        tries = 0
        while tries < max_tries:
            try:
                pw = getpass("CCMD password: ")

                # Verify based on hash type
                password_correct = False
                if is_bcrypt:
                    password_correct = bcrypt.checkpw(pw.encode(), hashed)
                elif is_pbkdf2:
                    password_correct = _verify_password_pbkdf2(pw, hashed)
                else:
                    print("ERROR: Unknown password hash format")
                    return False

                if password_correct:
                    # Success - cache it
                    _last_auth_ok["ts"] = time.time()
                    try:
                        username = os.getlogin()
                    except:
                        username = os.environ.get('USER', 'unknown')
                    log_auth_attempt(username, True)
                    return True
                else:
                    tries += 1
                    remaining = max_tries - tries
                    if remaining > 0:
                        print(f"Incorrect password. {remaining} attempt(s) remaining.")
                    else:
                        print("Incorrect password.")
            except KeyboardInterrupt:
                print("\nAuthentication cancelled")
                return False

        # All tries failed
        try:
            username = os.getlogin()
        except:
            username = os.environ.get('USER', 'unknown')
        log_auth_attempt(username, False)
        print("Authentication failed: maximum attempts exceeded")
        return False

    except Exception as e:
        print(f"Authentication error: {e}")
        return False


def verify_password(password: str) -> Tuple[bool, str]:
    """
    Programmatically verify password (non-interactive)

    Args:
        password: Password to verify

    Returns:
        Tuple of (is_valid, message)
    """
    if not HAS_BCRYPT:
        return True, "bcrypt not installed - auth bypassed"

    if not AUTH_FILE.exists():
        return False, "Master password not set"

    try:
        hashed = AUTH_FILE.read_bytes()
        if bcrypt.checkpw(password.encode(), hashed):
            return True, "Password correct"
        else:
            return False, "Password incorrect"
    except Exception as e:
        return False, f"Verification error: {e}"


def detect_sensitive_command(command: str) -> Tuple[bool, Optional[str]]:
    """
    Detect if a command contains sensitive patterns

    Args:
        command: Command string to check

    Returns:
        Tuple of (is_sensitive, reason)
    """
    for pattern in SENSITIVE_PATTERNS:
        if pattern.search(command):
            return True, f"Matched sensitive pattern: {pattern.pattern}"

    return False, None


def check_key_file_permissions(key_path: str) -> Tuple[bool, str]:
    """
    Validate SSH key file permissions

    Args:
        key_path: Path to SSH key file

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        path = Path(key_path).expanduser().resolve()

        # Check if file exists
        if not path.exists():
            return False, f"Key file not found: {path}"

        # Get file stats
        st = os.stat(path)

        # Check ownership (must be owned by current user)
        if st.st_uid != os.getuid():
            return False, "Key file not owned by current user"

        # Check permissions (must be 0600 or more restrictive)
        mode = stat.S_IMODE(st.st_mode)
        if mode & 0o177 != 0:  # Check if group/other have any permissions
            return False, f"Key file permissions too open: {oct(mode)} (require 0600)"

        return True, "Key file permissions OK"

    except Exception as e:
        return False, f"Permission check failed: {e}"


def extract_ssh_key_path(command: str) -> Optional[str]:
    """
    Extract SSH key path from command if present

    Args:
        command: Command string

    Returns:
        Path to SSH key if found, None otherwise
    """
    # Look for -i /path or -i /path or --identity /path
    patterns = [
        r"-i\s+(['\"]?)([/~][^'\"'\s]+)\1",
        r"--identity[=\s]+(['\"]?)([/~][^'\"'\s]+)\1",
    ]

    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(2)

    return None


def log_auth_attempt(user: str, success: bool):
    """
    Log authentication attempt

    Args:
        user: Username
        success: Whether authentication succeeded
    """
    try:
        # Ensure directory exists
        AUTH_LOG.parent.mkdir(parents=True, exist_ok=True)

        # Format log entry
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        status = "OK" if success else "FAIL"
        log_entry = f"{timestamp}\t{user}\t{status}\n"

        # Append to log
        with open(AUTH_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)

        # Set secure permissions (cross-platform)
        _set_secure_file_permissions(AUTH_LOG)

    except Exception:
        # Silently fail - don't break execution due to logging issues
        pass


def clear_auth_cache():
    """Clear the authentication cache"""
    _last_auth_ok["ts"] = 0


def get_auth_status() -> dict:
    """
    Get current authentication status

    Returns:
        Dictionary with auth status information
    """
    is_cached = time.time() - _last_auth_ok["ts"] < AUTH_CACHE_TTL
    has_password = AUTH_FILE.exists()

    return {
        'has_password': has_password,
        'is_cached': is_cached,
        'cache_ttl': AUTH_CACHE_TTL,
        'has_bcrypt': HAS_BCRYPT,
    }


def initialize_password_interactive() -> Tuple[bool, str]:
    """
    Interactive password initialization

    Returns:
        Tuple of (success, message)
    """
    if not HAS_BCRYPT:
        return False, "bcrypt not installed. Run: pip install bcrypt"

    if AUTH_FILE.exists():
        print("Master password already set.")
        reset = input("Do you want to reset it? (y/N): ").strip().lower()
        if reset not in ['y', 'yes']:
            return False, "Cancelled"

    print()
    print("Setting CCMD master password")
    print("This password will protect sensitive commands (SSH, sudo, etc.)")
    print()

    while True:
        pw1 = getpass("Enter master password (min 8 characters): ")
        if len(pw1) < 8:
            print("Password too short. Minimum 8 characters required.")
            continue

        pw2 = getpass("Confirm master password: ")
        if pw1 != pw2:
            print("Passwords do not match. Try again.")
            continue

        # Set password
        success, message = set_password(pw1)
        return success, message


def change_password_interactive() -> Tuple[bool, str]:
    """
    Change the master password (requires current password)

    Returns:
        Tuple of (success, message)
    """
    if not HAS_BCRYPT:
        return False, "bcrypt not installed. Run: pip install bcrypt"

    if not AUTH_FILE.exists():
        return False, "Master password not set. Run: init"

    print()
    print("Change CCMD master password")
    print()

    # Verify current password first
    try:
        current_pw = getpass("Enter current password: ")
        is_valid, msg = verify_password(current_pw)

        if not is_valid:
            return False, "Current password incorrect"

        print("✓ Current password verified")
        print()

    except KeyboardInterrupt:
        print("\nCancelled")
        return False, "Cancelled"

    # Get new password
    while True:
        try:
            pw1 = getpass("Enter new password (min 8 characters): ")
            if len(pw1) < 8:
                print("Password too short. Minimum 8 characters required.")
                continue

            pw2 = getpass("Confirm new password: ")
            if pw1 != pw2:
                print("Passwords do not match. Try again.")
                continue

            # Set new password
            success, message = set_password(pw1)
            if success:
                # Clear auth cache so new password takes effect
                clear_auth_cache()
            return success, message

        except KeyboardInterrupt:
            print("\nCancelled")
            return False, "Cancelled"


def reset_password_interactive() -> Tuple[bool, str]:
    """
    Reset (delete) the master password - requires explicit confirmation

    NOTE: v1.2.0 will add recovery key feature for more secure password reset

    Returns:
        Tuple of (success, message)
    """
    if not AUTH_FILE.exists():
        return False, "No master password set"

    print()
    print("⚠ FORGOT PASSWORD RESET")
    print()
    print(f"This will delete: {AUTH_FILE}")
    print("You must run 'init' to set a new password.")
    print()
    print("Alternative: You can also manually delete the file")
    print(f"  rm {AUTH_FILE}")
    print()
    print(f"NOTE: v1.2.0 will add recovery key feature for secure resets")
    print()

    try:
        confirmation = input("Type 'RESET' in capital letters to confirm: ").strip()

        if confirmation != 'RESET':
            return False, "Reset cancelled - confirmation did not match"

        # Delete the password file
        AUTH_FILE.unlink()

        # Clear the auth cache
        clear_auth_cache()

        # Also delete the log file if it exists (fresh start)
        if AUTH_LOG.exists():
            AUTH_LOG.unlink()

        return True, "Master password deleted successfully"

    except KeyboardInterrupt:
        print("\nCancelled")
        return False, "Cancelled"
    except Exception as e:
        return False, f"Failed to reset password: {e}"


# Export main functions
__all__ = [
    'set_password',
    'verify_password_interactive',
    'verify_password',
    'detect_sensitive_command',
    'check_key_file_permissions',
    'extract_ssh_key_path',
    'clear_auth_cache',
    'get_auth_status',
    'initialize_password_interactive',
    'change_password_interactive',
    'reset_password_interactive',
]
