# PLAIN v1.0.0 Release Checklist

Quick reference checklist for releasing PLAIN to the world.

## Pre-Release (1-2 weeks before)

### Code & Testing
- [ ] All critical bugs fixed (or documented as known issues)
- [ ] Run full test suite: `go test ./...`
- [ ] Test interpreter on all target platforms
- [ ] Test IDE on all target platforms
- [ ] Verify all example programs run correctly

### Documentation
- [ ] Update README.md status section (remove "In Development")
- [ ] Review and update docs/user/USER-GUIDE.md
- [ ] Review and update docs/user/TUTORIAL.md
- [ ] Review and update docs/user/LANGUAGE-REFERENCE.md
- [ ] Create/update CHANGELOG.md
- [ ] Write release notes

### Legal & Admin
- [ ] Add LICENSE file (decide: MIT, Apache 2.0, GPL, etc.)
- [ ] Add copyright notices to source files
- [ ] Update author/contact information
- [ ] Check for any sensitive data in repo (API keys, passwords, etc.)

### Version Management
- [ ] Update version in code (`plain --version` should work)
- [ ] Update version in IDE (About dialog)
- [ ] Update version in package files

## Build & Package (1 week before)

### Interpreter
- [ ] Run build script: `./scripts/build-release.sh 1.0.0`
- [ ] Verify binaries work on:
  - [ ] Linux (Ubuntu/Debian)
  - [ ] macOS (Intel)
  - [ ] macOS (Apple Silicon)
  - [ ] Windows 10/11

### IDE
- [ ] Package IDE for:
  - [ ] Linux (AppImage or installer)
  - [ ] macOS (DMG or .app bundle)
  - [ ] Windows (MSI or .exe installer)
- [ ] Test IDE installations on clean systems
- [ ] Verify IDE can find/launch interpreter

### Packaging
- [ ] All packages include:
  - [ ] Binary/executable
  - [ ] README.md
  - [ ] LICENSE
  - [ ] User documentation
  - [ ] Example programs
- [ ] Create checksums file
- [ ] Test extraction/installation on each platform

## Release Day

### GitHub Release
- [ ] Create and push tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
- [ ] Push to GitHub: `git push origin v1.0.0`
- [ ] Create GitHub Release:
  - [ ] Choose tag v1.0.0
  - [ ] Title: "PLAIN v1.0.0 - First Public Release"
  - [ ] Paste release notes
  - [ ] Upload all platform binaries
  - [ ] Upload checksums file
  - [ ] Mark as "Latest Release"
  - [ ] Publish!

### Website
- [ ] Update marketing-website with v1.0.0 announcement
- [ ] Add download buttons linking to GitHub releases
- [ ] Update screenshots/demos
- [ ] Deploy website updates

## Post-Release (First Week)

### Announcements
- [ ] Post to Reddit:
  - [ ] r/ProgrammingLanguages
  - [ ] r/programming (if allowed)
  - [ ] r/learnprogramming
- [ ] Post to Hacker News: "Show HN: PLAIN - A Programming Language..."
- [ ] Share on Twitter/X with #programming #education tags
- [ ] Share on LinkedIn
- [ ] Write blog post/article (Dev.to, Medium, personal blog)

### Community Setup
- [ ] Enable GitHub Discussions
- [ ] Set up GitHub Issues templates
- [ ] Create CONTRIBUTING.md guide
- [ ] Monitor and respond to:
  - [ ] GitHub issues
  - [ ] Pull requests
  - [ ] Discussion threads
  - [ ] Social media mentions

### Documentation
- [ ] Add installation instructions based on user feedback
- [ ] Create FAQ based on common questions
- [ ] Create video tutorials (optional but recommended)

## Success Metrics (First Month)

Track these metrics:
- [ ] GitHub stars: _____
- [ ] Download count: _____
- [ ] Issues opened: _____
- [ ] Issues resolved: _____
- [ ] Contributors: _____
- [ ] Website visitors: _____

## Known Issues to Document

**Great news!** All 10 defects identified during tutorial creation have been fixed! ✅

No critical known issues at this time. Any issues discovered after release should be:
- Documented in GitHub Issues
- Added to CHANGELOG.md for the next release
- Listed in release notes if they affect v1.0.0

---

## Quick Commands Reference

```bash
# Build all releases
./scripts/build-release.sh 1.0.0

# Create git tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Test interpreter
go test ./...

# Run interpreter
./plain examples/hello.plain

# Run IDE
cd plain_ide && python main.py
```

---

## Emergency Rollback Plan

If critical issues are discovered after release:

1. Mark GitHub release as "Pre-release"
2. Add warning to README
3. Post issue on GitHub
4. Prepare hotfix v1.0.1
5. Test thoroughly
6. Release v1.0.1 as soon as possible

---

## Post-v1.0 Roadmap Planning

After successful v1.0 release, plan for:

- [ ] v1.0.1 - Bug fixes based on user feedback
- [ ] v1.1.0 - Fix defects 2-5, 7
- [ ] v1.2.0 - New features from community requests
- [ ] v2.0.0 - Major improvements/breaking changes
