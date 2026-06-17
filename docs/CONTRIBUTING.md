# Contributing to CCMD

Thank you for your interest in contributing to CCMD! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Security Guidelines](#security-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to Robert5560newton@gmail.com.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/Wisyle/ccmd/issues) to avoid duplicates.

When creating a bug report, include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Detailed steps to reproduce the behavior
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**: OS, Python version, CCMD version, shell type
- **Logs**: Relevant error messages or logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use case**: Describe the problem this enhancement would solve
- **Proposed solution**: Describe how you envision the enhancement working
- **Alternatives**: Describe any alternative solutions you've considered
- **Additional context**: Any other context, screenshots, or examples

### Security Vulnerabilities

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email: **Robert5560newton@gmail.com**
2. Include: Detailed description, steps to reproduce, potential impact
3. Wait for response (within 48 hours)
4. Follow responsible disclosure guidelines

See our [Security Policy](SECURITY.md) for more details.

## Development Setup

### Prerequisites

- Python 3.7+
- Git
- pip and build tools

### Clone and Setup

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/ccmd.git
cd ccmd
git checkout -b feature/your-feature-name

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ccmd --cov-report=html

# Run security scans
bandit -r ccmd/
safety check -r requirements.txt
```

## Security Guidelines

### Critical Security Rules

1. **Never use `shell=True`** in subprocess calls unless absolutely necessary
   - If required, document WHY in code comments
   - Add to whitelist in security lint workflow

2. **Validate all user input** before execution
   - Use `CommandSecurityValidator` from `ccmd/core/security.py`
   - Block dangerous patterns (command injection, path traversal, etc.)

3. **Handle credentials securely**
   - Never log passwords or API tokens
   - Use bcrypt for password hashing
   - Implement proper file permissions (0600 for sensitive files)

4. **Protect against common vulnerabilities**
   - Path traversal: Validate file paths
   - Command injection: Sanitize shell commands
   - Dependency vulnerabilities: Pin versions

### Security Checklist for PRs

Before submitting security-related PRs:

- [ ] Ran `bandit -r ccmd/` with 0 HIGH issues
- [ ] Ran `safety check` with 0 vulnerabilities
- [ ] Updated SECURITY_CHANGELOG.md
- [ ] Added tests for security validations
- [ ] Documented security considerations in code
- [ ] No hardcoded secrets or credentials

## Pull Request Process

### 1. Create Your Branch

```bash
git checkout -b feature/amazing-feature
# or
git checkout -b fix/bug-description
# or
git checkout -b security/vulnerability-fix
```

### 2. Make Your Changes

- Write clear, concise code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest

# Check code quality
bandit -r ccmd/
safety check

# Test installation
pip install -e .
ccmd --version
ccmd --list
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "type: brief description

Detailed explanation of changes (if needed)
"
```

**Commit Message Format:**

- `feat:` New feature
- `fix:` Bug fix
- `security:` Security improvement
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring

### 5. Push and Create PR

```bash
git push origin feature/amazing-feature
```

Then create a Pull Request on GitHub with:

- **Clear title**: Describe what the PR does
- **Description**: Why the change is needed
- **Testing**: How you tested the changes
- **Screenshots**: If UI/output changes
- **Related issues**: Link to related issues

### 6. PR Review Process

- Maintainers will review your PR within 1 week
- Address feedback promptly
- Once approved, maintainers will merge

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

### Example:

```python
def validate_command(command: str, context: str = "default") -> tuple[bool, str]:
    """
    Validate command for security issues.

    Args:
        command: The command string to validate
        context: Execution context (default, custom, system)

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_command("ls -la")
        (True, "")
        >>> validate_command("rm -rf /")
        (False, "Dangerous pattern detected")
    """
    # Implementation
    pass
```

### File Organization

```
ccmd/
├── core/          # Core logic (no CLI dependencies)
├── cli/           # CLI-specific code
└── __init__.py    # Package metadata
```

### Security Code Review

For security-sensitive code:

1. **Comment WHY**, not just WHAT
2. **Reference CVEs or security advisories** if applicable
3. **Add tests** that attempt to bypass security measures
4. **Document** in SECURITY_CHANGELOG.md

## Testing

### Test Coverage

- Aim for 80%+ code coverage
- All security features must have tests
- Test edge cases and error conditions

### Writing Tests

```python
# tests/test_security.py
def test_blocks_command_injection():
    """Ensure command injection attempts are blocked."""
    from ccmd.core.security import CommandSecurityValidator

    dangerous = "; rm -rf /"
    is_valid, error = CommandSecurityValidator.validate_command(dangerous)

    assert not is_valid
    assert "dangerous pattern" in error.lower()
```

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_security.py

# Run specific test function
pytest tests/test_security.py::test_blocks_command_injection

# Run with verbose output
pytest -v
```

## Documentation

### Update Documentation When:

- Adding new features
- Changing existing behavior
- Fixing bugs
- Improving security

### Documentation Files to Update:

- `README.md` - User-facing features
- `FEATURES.md` - Comprehensive feature list
- `SECURITY.md` - Security-related changes
- `ARCHITECTURE.md` - Structural changes
- Docstrings in code

### Documentation Style

- Be clear and concise
- Include code examples
- Explain WHY, not just HOW
- Update version references

## Getting Help

### Resources

- **Documentation**: https://github.com/Wisyle/ccmd
- **Issues**: https://github.com/Wisyle/ccmd/issues
- **Security**: Robert5560newton@gmail.com
- **Discussions**: GitHub Discussions (if enabled)

### Questions?

- Check existing [issues](https://github.com/Wisyle/ccmd/issues)
- Read the [documentation](https://github.com/Wisyle/ccmd#readme)
- Ask in your PR or issue

## Recognition

Contributors will be:

- Listed in release notes
- Credited in GitHub contributors page
- Mentioned in security advisories (if applicable)

## License

By contributing to CCMD, you agree that your contributions will be licensed under the MIT License.

---

## Quick Contribution Checklist

Before submitting your PR, ensure:

- [ ] Code follows Python PEP 8 style guide
- [ ] Tests added for new features
- [ ] All tests passing (`pytest`)
- [ ] Security scans passing (`bandit`, `safety`)
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] PR description is comprehensive
- [ ] No merge conflicts with main branch
- [ ] Security guidelines followed (if applicable)

Thank you for contributing to CCMD! 🎉

---

**Maintainer:** De Catalyst (@Wisyle)
**Contact:** Robert5560newton@gmail.com
**Project:** https://github.com/Wisyle/ccmd
