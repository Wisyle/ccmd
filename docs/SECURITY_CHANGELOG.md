# Security Changelog

This document tracks all security-related changes to CCMD. Each entry includes the version, date, and detailed description of security improvements or fixes.

## v1.1.5 (2025-10-30)

### HIGH Priority Fixes
- **FIX:** --exec flag exposure vulnerability
  - Hidden --exec from public help text using argparse.SUPPRESS
  - Added CCMD_INTERNAL environment variable gate
  - Only internal command chaining can call --exec
  - External calls blocked with clear error message
  - Lines: ccmd/cli/main.py:308-309, ccmd/cli/main.py:967-982, ccmd/core/executor.py:509-520

### MEDIUM Priority Improvements
- **ADD:** Atomic shell config writes (prevents corruption)
  - Write to temp file first
  - Atomic rename using os.replace()
  - Automatic backup before modification
  - Auto-recovery on failure
  - Shell syntax validation (optional)
  - Lines: ccmd/core/rollback.py:219-380

- **ADD:** Path diagnostics command (--check-paths)
  - Validates CCMD_HOME environment variable
  - Checks installation directory exists
  - Verifies run.py and commands.yaml present
  - Tests shell integration
  - Reports backup status
  - Lines: ccmd/cli/main.py:576-710

- **ENHANCE:** Improved safe_file_edit with atomic writes
  - Now uses atomic writes by default for shell configs
  - Optional validation function support
  - Better error handling with auto-recovery
  - Lines: ccmd/core/rollback.py:395-450

### Documentation
- **ADD:** THREAT_MODEL.md
  - Complete threat analysis
  - Attack scenarios and mitigations
  - Security design principles
  - What CCMD protects against vs what it doesn't
  - Incident response procedures

- **ADD:** RECOVERY.md
  - Emergency recovery procedures
  - Step-by-step troubleshooting
  - Shell config restoration guide
  - Manual removal instructions
  - Platform-specific recovery (Linux/Mac/Windows/WSL)

- **UPDATE:** Enhanced security documentation
  - Expanded threat coverage
  - Added recovery procedures
  - Documented new security features

### Security Infrastructure
- **ADD:** Dependabot configuration
  - Weekly dependency vulnerability scanning
  - Automated pull requests for security updates
  - Python and GitHub Actions monitoring
  - Lines: .github/dependabot.yml

- **ENHANCE:** Security linting workflow
  - Added Safety dependency scanner
  - Checks for known vulnerabilities in requirements.txt
  - Integrated with existing Bandit scans
  - Lines: .github/workflows/security_lint.yml:50-55

### Security Improvements Summary

**Before v1.1.5:**
- --exec flag publicly accessible (anyone could call it)
- Shell config writes not atomic (corruption possible)
- No path diagnostics (hard to troubleshoot)
- No dependency vulnerability monitoring
- Limited recovery documentation

**After v1.1.5:**
- ✅ --exec protected by environment gate
- ✅ Atomic writes prevent corruption
- ✅ --check-paths diagnoses issues
- ✅ Dependabot monitors vulnerabilities
- ✅ Comprehensive recovery guide

### Metrics
- Bandit scan: 0 HIGH, 5 MEDIUM, 38 LOW (maintained)
- Safety scan: 0 vulnerabilities (maintained)
- New features: 4 (--check-paths, atomic writes, THREAT_MODEL, RECOVERY)
- Documentation: +2 files (THREAT_MODEL.md, RECOVERY.md)
- Security tests: All passing

### Acknowledgments
- Security audit feedback from community reviewer (October 30, 2025)
- Recommendations implemented: 7/7 items addressed

---

## v1.1.4 (2025-10-30)

### HIGH Priority Fixes
- **FIX:** Tarfile path traversal vulnerability (CVE-2007-4559)
  - Added member validation before extraction
  - Checks for absolute paths and parent directory references
  - Validates all paths remain within extraction directory
  - Line: ccmd/cli/main.py:443-470

- **FIX:** URL scheme validation for urllib operations
  - Added HTTPS-only validation for all URL operations  
  - Prevents file:// and other scheme attacks
  - Lines: ccmd/cli/main.py:411,435,689

### MEDIUM Priority Fixes
- **FIX:** Pinned GitPython to v3.1.43
  - Avoids 6 known vulnerabilities in unpinned versions
  - Line: requirements.txt:11

### Documentation
- **ADD:** Security documentation for subprocess shell=True usage
  - Detailed explanation of why it's required for system commands
  - Clear security boundaries between system and user commands
  - Line: ccmd/core/executor.py:325-334

### Security Infrastructure
- **ADD:** GitHub CodeQL analysis workflow
- **ADD:** Security linting GitHub Action
- **ADD:** SECURITY.md with vulnerability reporting process
- **ADD:** Automated Bandit and Safety scanning

### Metrics
- Bandit scan: 0 HIGH (down from 2), 5 MEDIUM, 38 LOW
- Safety scan: 0 vulnerabilities
- Code coverage: ~60% (estimated)

---

## v1.1.3 (2025-10-29)
- **FIX:** Multiple timeout handling improvements
- **ADD:** Command execution timeout controls

## v1.1.2 (2025-10-27) 
- **FIX:** bcrypt bypass vulnerability - Added PBKDF2 fallback
- **FIX:** Custom command type abuse - Force type='custom'
- **FIX:** Incomplete sensitive pattern detection - Expanded to 40+ patterns
- **FIX:** Command chaining bypass - Block &&, ||, ;, backticks, $()

## v1.1.1 (2025-10-27)
- **ADD:** Master password system with bcrypt
- **ADD:** Command injection prevention
- **ADD:** SSH key validation  
- **ADD:** Sensitive command auto-detection

## v1.1.0 (2025-10-20)
- **ADD:** Interactive mode security controls
- **ADD:** Input sanitization
- **ADD:** Rollback system for safe updates

## v1.0.0 (2025-10-01)
- Initial release with basic security measures
- Shell command validation
- Safe subprocess execution

---

*This changelog is maintained to track security improvements and provide transparency about CCMD's security posture.*