# Security Changelog

This document tracks all security-related changes to CCMD. Each entry includes the version, date, and detailed description of security improvements or fixes.

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