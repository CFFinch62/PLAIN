# Setting Up Private GitHub Repository for PLAIN

## Step-by-Step Guide

### 1. Create Private Repository on GitHub

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name:** `plain-language` (or your preferred name)
   - **Description:** `PLAIN Programming Language - Able, Intuitive, and Natural`
   - **Visibility:** ⚠️ **Select "Private"** (this is critical!)
   - **Initialize repository:** Leave ALL checkboxes UNCHECKED
     - [ ] Do NOT add README
     - [ ] Do NOT add .gitignore
     - [ ] Do NOT choose a license

3. Click **"Create repository"**

### 2. Connect Your Local Repository

You should see a page with setup instructions. Use the "push an existing repository" option:

```bash
# Check your current remote (if any)
git remote -v

# If you don't have a remote called 'origin', add it:
git remote add origin https://github.com/YOUR-USERNAME/plain-language.git

# If you already have an 'origin', update its URL:
git remote set-url origin https://github.com/YOUR-USERNAME/plain-language.git

# Push your code to GitHub
git push -u origin main

# Push all tags
git push --tags
```

**Replace `YOUR-USERNAME` with your actual GitHub username!**

### 3. Verify Privacy Settings

After pushing:

1. Go to your repository on GitHub
2. You should see a 🔒 **Private** badge next to the repository name
3. Check Settings → General → Danger Zone
4. Confirm "Change repository visibility" shows "Private"

### 4. Configure Repository Settings

**Enable Discussions (Optional):**
1. Settings → General
2. Scroll to "Features"
3. Check ✅ "Discussions"
4. Good for: Beta tester feedback, Q&A

**Enable Issues:**
1. Should be enabled by default
2. Used for: Bug reports, feature requests

**Disable Wiki (Recommended):**
1. Settings → General → Features
2. Uncheck "Wikis"
3. Why: You have comprehensive docs/ already

**Branch Protection (Optional but Recommended):**
1. Settings → Branches
2. Add rule for `main` branch:
   - ✅ Require pull request reviews before merging
   - ✅ Dismiss stale pull request approvals when new commits are pushed
3. Protects against accidental pushes to main

### 5. Add Collaborators (Beta Testers)

When ready to add beta testers:

1. Settings → Collaborators and teams
2. Click "Add people"
3. Enter GitHub username or email
4. Choose permission level:
   - **Read:** Can view code and create issues (for beta testers)
   - **Write:** Can push code (for trusted contributors)
   - **Admin:** Full access (only for co-maintainers)

**Recommended for beta testers:** Read access only

### 6. Create First Private Release

Once code is pushed:

1. Go to repository → Releases
2. Click "Draft a new release"
3. Fill in:
   - **Tag:** `v1.0.0-beta1`
   - **Title:** `PLAIN v1.0.0 Beta 1 - Private Release`
   - **Description:**
     ```markdown
     # PLAIN v1.0.0 Beta 1

     Private beta release for invited testers only.

     ## What's Included
     - PLAIN interpreter (all platforms)
     - PLAIN IDE
     - Documentation
     - Example programs

     ## Installation
     See README.md for installation instructions.

     ## Reporting Issues
     Please report bugs via GitHub Issues.

     ## Beta Agreement
     By downloading, you agree to the terms in the LICENSE file.
     ```
   - **This is a pre-release:** ✅ Check this box
   - **Attach binaries:** Upload files from `releases/` folder

4. Click "Publish release"

**Note:** Only collaborators can see private releases!

### 7. Security Best Practices

**Add .gitignore (if not already present):**
```
# Binaries
plain
plain.exe
*.exe
*.dll
*.so
*.dylib

# Test binary
*.test

# Output of the go coverage tool
*.out
coverage.out

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build artifacts
releases/
dist/
build/

# Python (for IDE)
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
venv/
env/

# Secrets (important!)
.env
*.key
*.pem
secrets/
credentials/
```

**Never commit:**
- API keys or tokens
- Personal information
- Production credentials
- Large binary files (use releases instead)

### 8. GitHub CLI (Optional)

For easier repository management, install GitHub CLI:

```bash
# Install gh CLI (macOS)
brew install gh

# Install gh CLI (Windows - Chocolatey)
choco install gh

# Install gh CLI (Linux)
# See: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Authenticate
gh auth login

# Create release from command line
gh release create v1.0.0-beta1 \
  releases/*.tar.gz releases/*.zip \
  --title "PLAIN v1.0.0 Beta 1" \
  --notes "Private beta release" \
  --prerelease

# Add collaborators from command line
gh api repos/YOUR-USERNAME/plain-language/collaborators/THEIR-USERNAME \
  -X PUT -f permission=read
```

### 9. Backup Strategy

Even with GitHub, maintain local backups:

```bash
# Create a backup
tar -czf plain-backup-$(date +%Y%m%d).tar.gz \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='releases' \
  .

# Or use git bundle (includes full history)
git bundle create plain-backup-$(date +%Y%m%d).bundle --all
```

### 10. Monitoring

**Watch for:**
- Star count (even private repos can be starred by collaborators)
- Fork count
- Issue activity
- Clone activity (Settings → Insights → Traffic)

**GitHub Insights:**
- Settings → Insights → Traffic: See clones and visitors
- Settings → Insights → Community: Check repository health

---

## Troubleshooting

### "Repository not found" when pushing
- Verify you're using the correct repository URL
- Check you're logged into the right GitHub account
- Confirm repository exists and is accessible to you

### Can't see private releases
- Only collaborators can see private releases
- Make sure you're logged into GitHub
- Check repository visibility is "Private"

### Collaborators can't access
- Verify they accepted the invitation (check their email)
- Confirm you added them to the correct repository
- Check they're using the GitHub account you invited

### Want to transfer ownership later
- Settings → Danger Zone → Transfer ownership
- Can transfer to organization or another user
- Maintains all history, issues, releases

---

## Quick Reference Commands

```bash
# Check current remote
git remote -v

# Add remote
git remote add origin https://github.com/YOUR-USERNAME/plain-language.git

# Push code
git push -u origin main

# Push tags
git push --tags

# Create and push new tag
git tag -a v1.0.0-beta1 -m "Beta 1 release"
git push origin v1.0.0-beta1

# Pull latest changes
git pull origin main

# Check repository status
git status

# See commit history
git log --oneline -10
```

---

## Next Steps After Setup

1. ✅ Repository created and pushed
2. [ ] Create v1.0.0-beta1 release with binaries
3. [ ] Invite 5-10 trusted beta testers
4. [ ] Enable GitHub Discussions for feedback
5. [ ] Create issue templates for bug reports
6. [ ] Set up project board for tracking work (optional)
7. [ ] Deploy marketing website
8. [ ] Create beta signup form

---

## When You're Ready to Go Public

**To make repository public later:**

1. Settings → General
2. Scroll to "Danger Zone"
3. Click "Change repository visibility"
4. Select "Public"
5. Type repository name to confirm
6. Click "I understand, change repository visibility"

⚠️ **Warning:** This cannot be easily undone! Once code is public, it's out there forever (even if you make it private again, people may have cloned it).

**Before going public:**
- Review all code for sensitive data
- Update LICENSE to open source license (MIT, Apache, etc.)
- Clean up commit history if needed
- Prepare announcement
- Update README with public information
