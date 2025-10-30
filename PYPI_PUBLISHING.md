# PyPI Publishing Guide for CCMD

This guide explains how to publish updates to CCMD on PyPI whenever you release bug fixes, new features, or security patches.

## 📦 Overview

CCMD is published on PyPI at: https://pypi.org/project/ccmd/

Users install it with: `pip install ccmd`

## 🔄 Publishing a New Version

Follow these steps **every time** you want to release a new version:

### Step 1: Update Version Number

Edit `ccmd/__init__.py`:

```python
__version__ = "1.1.5"  # Increment version
__author__ = "De Catalyst"
```

### Step 2: Update pyproject.toml

Edit `pyproject.toml`:

```toml
[project]
name = "ccmd"
version = "1.1.5"  # Must match __init__.py
description = "Cross-platform Command Manager - Simplify your terminal with intuitive shortcuts"
```

**IMPORTANT:** Version must match exactly between `__init__.py` and `pyproject.toml`

### Step 3: Update Documentation

Update these files with the new version:

1. **README.md** - Update version notice and features
2. **RELEASE_NOTES_v{version}.md** - Create new release notes
3. **SECURITY_CHANGELOG.md** - If security-related changes

### Step 4: Clean Previous Builds

Remove old build artifacts:

```bash
rm -rf dist/ build/ *.egg-info/
```

### Step 5: Build the Package

```bash
python3 -m build
```

This creates:
- `dist/ccmd-{version}-py3-none-any.whl` (wheel file)
- `dist/ccmd-{version}.tar.gz` (source distribution)

### Step 6: Verify the Build

```bash
python3 -m twine check dist/*
```

Expected output: `PASSED` for both files

### Step 7: Upload to PyPI

```bash
python3 -m twine upload dist/*
```

**Note:** This uses credentials from `~/.pypirc` (configured during initial setup)

### Step 8: Verify on PyPI

Check that your new version is live:

```bash
# Check PyPI page
curl -s https://pypi.org/pypi/ccmd/json | python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])"

# Or visit directly
open https://pypi.org/project/ccmd/
```

### Step 9: Test Installation

Test that users can install the new version:

```bash
# Create test environment
python3 -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install ccmd

# Test it works
ccmd --version

# Cleanup
deactivate
rm -rf test_env
```

### Step 10: Git Commit and Tag

```bash
# Commit changes
git add ccmd/__init__.py pyproject.toml README.md RELEASE_NOTES_v{version}.md
git commit -m "release: v{version}"

# Create git tag
git tag -a v{version} -m "Release v{version}"

# Push to GitHub
git push origin ccmd && git push origin v{version}
```

### Step 11: Create GitHub Release

Go to https://github.com/Wisyle/ccmd/releases/new

- Tag: `v{version}`
- Title: `v{version} - {Release Name}`
- Body: Copy from `RELEASE_NOTES_v{version}.md`
- Publish release

---

## 📋 Quick Checklist

Use this checklist for every release:

- [ ] Update `ccmd/__init__.py` version
- [ ] Update `pyproject.toml` version
- [ ] Update README.md
- [ ] Create RELEASE_NOTES_v{version}.md
- [ ] Update SECURITY_CHANGELOG.md (if applicable)
- [ ] Clean old builds: `rm -rf dist/ build/ *.egg-info/`
- [ ] Build package: `python3 -m build`
- [ ] Verify build: `python3 -m twine check dist/*`
- [ ] Upload to PyPI: `python3 -m twine upload dist/*`
- [ ] Verify on PyPI webpage
- [ ] Test installation: `pip install ccmd`
- [ ] Commit changes
- [ ] Create git tag
- [ ] Push to GitHub
- [ ] Create GitHub release

---

## 🔢 Version Numbering

CCMD uses semantic versioning: `MAJOR.MINOR.PATCH`

### When to increment:

- **PATCH** (1.1.4 → 1.1.5)
  - Bug fixes
  - Security patches
  - Documentation updates
  - No breaking changes

- **MINOR** (1.1.5 → 1.2.0)
  - New features
  - Non-breaking enhancements
  - New commands added
  - Backward compatible

- **MAJOR** (1.2.0 → 2.0.0)
  - Breaking changes
  - Major rewrites
  - API changes
  - Not backward compatible

### Examples:

```
v1.1.4 → v1.1.5  (Security patch)
v1.1.5 → v1.2.0  (New recovery key feature)
v1.2.0 → v2.0.0  (Complete rewrite)
```

---

## 🐛 Hotfix Releases

For urgent security fixes:

1. **Work on a hotfix branch:**
   ```bash
   git checkout -b hotfix-v1.1.5
   ```

2. **Make minimal changes** (only the fix)

3. **Follow all steps above** but faster

4. **Merge to main:**
   ```bash
   git checkout ccmd
   git merge hotfix-v1.1.5
   git push origin ccmd
   ```

---

## 🧪 Testing Before Publishing

### Local Testing

Before uploading to PyPI, test locally:

```bash
# Build package
python3 -m build

# Install locally
pip install dist/ccmd-{version}-py3-none-any.whl

# Test
ccmd --version
ccmd --list
go home
```

### TestPyPI (Optional)

For major releases, test on TestPyPI first:

```bash
# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ ccmd

# Test thoroughly
ccmd --version
```

---

## ⚠️ Common Issues

### Issue 1: "File already exists"

**Problem:** Trying to upload a version that already exists on PyPI

**Solution:** Increment version number (can't overwrite existing versions)

### Issue 2: "Invalid credentials"

**Problem:** PyPI token expired or incorrect

**Solution:**
1. Go to https://pypi.org/manage/account/token/
2. Revoke old token
3. Create new token
4. Update `~/.pypirc`:
   ```
   [pypi]
   username = __token__
   password = pypi-YOUR_NEW_TOKEN_HERE
   ```

### Issue 3: "Version mismatch"

**Problem:** `__init__.py` version doesn't match `pyproject.toml`

**Solution:** Make sure both files have identical version numbers

### Issue 4: Package doesn't include commands.yaml

**Problem:** MANIFEST.in not including necessary files

**Solution:** Verify MANIFEST.in includes:
```
include commands.yaml
```

---

## 🎯 Best Practices

1. **Always test locally before publishing**
2. **Never skip version increments** (1.1.4 → 1.1.5, not 1.1.4 → 1.1.6)
3. **Update documentation before building**
4. **Create release notes for every version**
5. **Tag commits with version numbers**
6. **Verify PyPI page after upload**
7. **Test actual pip installation**
8. **Keep SECURITY_CHANGELOG.md updated**

---

## 📞 Help

If you encounter issues:

1. Check PyPI status: https://status.python.org/
2. Review Twine docs: https://twine.readthedocs.io/
3. Check packaging guide: https://packaging.python.org/

---

## 📝 Example Workflow

Here's a complete example for releasing v1.1.5 with a bug fix:

```bash
# 1. Update version
vim ccmd/__init__.py  # Change to 1.1.5
vim pyproject.toml    # Change to 1.1.5

# 2. Update docs
vim README.md
vim RELEASE_NOTES_v1.1.5.md

# 3. Clean and build
rm -rf dist/ build/ *.egg-info/
python3 -m build

# 4. Verify
python3 -m twine check dist/*

# 5. Upload
python3 -m twine upload dist/*

# 6. Verify on PyPI
curl -s https://pypi.org/pypi/ccmd/json | grep '"version"'

# 7. Test installation
pip install --upgrade ccmd
ccmd --version  # Should show 1.1.5

# 8. Git commit and tag
git add .
git commit -m "release: v1.1.5 bug fixes"
git tag -a v1.1.5 -m "Release v1.1.5"
git push origin ccmd && git push origin v1.1.5

# 9. Create GitHub release at:
# https://github.com/Wisyle/ccmd/releases/new
```

---

**Last Updated:** October 30, 2025
**Current Version:** 1.1.4
**PyPI Page:** https://pypi.org/project/ccmd/
