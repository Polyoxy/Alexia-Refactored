# Alexia Release Process

## 📋 Release Checklist

### 1. Prepare for Release

- [ ] Review open issues and PRs
- [ ] Update changelog
- [ ] Run all tests
- [ ] Update version number
- [ ] Update documentation

### 2. Create Release Branch

```bash
git checkout -b release/vX.Y.Z
```

### 3. Update Version

1. Update `__version__` in `alexia/__init__.py`
2. Update version in `setup.py`
3. Update version in `docs/conf.py`

### 4. Update Changelog

1. Document all changes since last release
2. Categorize changes:
   - 🚀 Features
   - 🐛 Bug Fixes
   - 📚 Documentation
   - 🛠️ Maintenance
   - 🔧 Configuration

### 5. Create Release Notes

```markdown
## vX.Y.Z (YYYY-MM-DD)

### 🚀 Features

- Feature 1
- Feature 2

### 🐛 Bug Fixes

- Fix 1
- Fix 2

### 📚 Documentation

- Doc Update 1
- Doc Update 2
```

### 6. Create Pull Request

1. Target `main` branch
2. Title: `release/vX.Y.Z`
3. Add release notes
4. Request review

### 7. Merge and Tag

```bash
git checkout main
git merge release/vX.Y.Z
git tag vX.Y.Z
git push origin main --tags
```

### 8. Create GitHub Release

1. Go to GitHub Releases
2. Create new release
3. Use tag `vX.Y.Z`
4. Add release notes
5. Publish release

### 9. Post-Release Tasks

- [ ] Update dependencies
- [ ] Update documentation
- [ ] Close milestone
- [ ] Update roadmap
- [ ] Announce release
