# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

**DO NOT** open public issues for security vulnerabilities.

### Reporting Channel
**Email:** Robert5560newton@gmail.com  
**Response Time:** Within 48 hours  

### What to Include
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)
- Your contact information

## Security Measures

CCMD implements multiple security layers:

### Command Injection Prevention
- ✅ 35+ dangerous patterns blocked
- ✅ Shell metacharacter validation
- ✅ Command chaining prevention (&&, ||, ;)
- ✅ Backtick and $() execution blocking
- ✅ Path traversal protection

### Authentication & Authorization
- ✅ bcrypt password hashing (100k iterations)
- ✅ PBKDF2 fallback for compatibility
- ✅ Master password protection for sensitive commands
- ✅ Secure password storage with file permissions (0600)

### Execution Safety
- ✅ shell=False enforcement for user commands
- ✅ 180s timeout for non-interactive commands
- ✅ Input sanitization for all commands
- ✅ Context-aware command validation
- ✅ Type enforcement for custom commands

### SSH & Key Management
- ✅ SSH key permission validation
- ✅ Encrypted SSH key storage
- ✅ Key fingerprint verification

### File Operations
- ✅ Atomic file operations
- ✅ Safe backup and rollback system
- ✅ Permission checks before operations

## Security Audits

### Self-Audits
- **2025-10-30** Bandit scan: 2 HIGH, 5 MEDIUM, 38 LOW issues identified
- **2025-10-30** Safety check: 0 vulnerabilities (6 ignored in unpinned packages)
- **2025-10-30** CodeQL scan: Pending setup

### Community Audits
- *No community audits yet - [Contact us](#reporting-a-vulnerability) to contribute*

### Professional Audits
- *Planned for Q1 2026 - Contributions welcome*

## Vulnerability Disclosure Timeline

We aim to:
1. **Acknowledge report** within 48 hours
2. **Provide initial assessment** within 1 week
3. **Release patch** within 2 weeks (for HIGH/CRITICAL)
4. **Public disclosure** 30 days after patch release

## Security Update Process

1. Security issues are prioritized above feature requests
2. Patches are released as soon as possible
3. All users are notified through GitHub releases
4. Security changelog is maintained in SECURITY_CHANGELOG.md

## Known Security Considerations

### Current Issues Being Addressed
1. **Tarfile extraction without validation** (HIGH) - Fix planned for v1.1.3
2. **subprocess with shell=True for system commands** (HIGH) - Under review
3. **URL open without scheme validation** (MEDIUM) - Fix planned for v1.1.3

### Design Decisions
- System commands require shell=True for proper expansion
- Interactive commands inherit terminal for user interaction
- Master password uses bcrypt with PBKDF2 fallback for compatibility

## Security Best Practices for Users

1. **Keep CCMD Updated** - Always use the latest version
2. **Use Strong Master Password** - Minimum 8 characters recommended
3. **Review Custom Commands** - Audit any custom commands before adding
4. **Limit SSH Key Access** - Only add necessary SSH keys
5. **Regular Backups** - Use the rollback feature for safety

## Hall of Fame

Security researchers who have helped improve CCMD:
- *Be the first contributor! Report a vulnerability to get listed here*

## Contact

**Security Lead:** De Catalyst (@Wisyle)  
**Email:** Robert5560newton@gmail.com  
**Twitter:** [@iamdecatalyst](https://x.com/iamdecatalyst)  
**GitHub:** [@Wisyle](https://github.com/Wisyle)

---

*This security policy is updated regularly. Last update: 2025-10-30*