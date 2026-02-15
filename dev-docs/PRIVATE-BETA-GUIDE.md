# Private Beta Testing Guide

How to run a private beta program while keeping your code proprietary.

---

## Overview

**Goal:** Get real-world testing and feedback without sharing source code

**Approach:** Distribute compiled binaries only to trusted testers

**Protection:** Beta tester agreement + private distribution

---

## Step 1: Prepare Your Repository

### Make Repository Private

If your GitHub repo is currently public:

1. Go to GitHub → Your Repository → Settings
2. Scroll to "Danger Zone"
3. Click "Change visibility"
4. Select "Make private"
5. Confirm

**Important:** This makes the SOURCE CODE private, but you can still share compiled releases.

---

## Step 2: Build Your Releases

On each platform (Linux, Mac, Windows):

```bash
# Linux/Mac
./scripts/build-release.sh 1.0.0-beta1

# Windows
scripts\build-release.bat 1.0.0-beta1
```

You'll have:
- `plain-v1.0.0-beta1-linux-amd64.tar.gz`
- `plain-v1.0.0-beta1-darwin-amd64.tar.gz`
- `plain-v1.0.0-beta1-darwin-arm64.tar.gz`
- `plain-v1.0.0-beta1-windows-amd64.zip`

**These are compiled binaries - NO source code included!**

---

## Step 3: Create Private Release

### Option A: GitHub Private Release (Recommended)

```bash
# Create and push tag
git tag v1.0.0-beta1
git push origin v1.0.0-beta1

# On GitHub:
# 1. Go to Releases → Draft new release
# 2. Choose tag: v1.0.0-beta1
# 3. Title: "PLAIN v1.0.0-beta1 - Private Beta"
# 4. Upload all 4 compiled archives
# 5. Add release notes (see template below)
# 6. ✅ Check "Set as a pre-release"
# 7. Publish release
```

**Important:** Even though the repo is private, you can share the release download links with specific people.

### Option B: Dropbox/Google Drive

1. Upload the 4 archives to a folder
2. Create a password-protected shared link
3. Share link + password with testers

### Option C: Your Own Server

1. Upload to your web server
2. Create password-protected directory
3. Share URL + credentials with testers

---

## Step 4: Invite Beta Testers

### Create Invitation Email Template

```
Subject: Invitation to PLAIN Beta Testing Program

Hi [Name],

You're invited to participate in the private beta testing program for PLAIN, 
a new programming language designed for education and clarity.

WHAT YOU'LL GET:
- Early access to PLAIN interpreter and IDE
- Opportunity to influence the language's development
- Recognition in the final release (if you'd like)

WHAT WE NEED FROM YOU:
- Test the software on your platform (Windows/Mac/Linux)
- Report bugs and issues
- Provide feedback on the language design and IDE
- Keep the software confidential (this is proprietary software)

NEXT STEPS:
1. Read and accept the Beta Tester Agreement (attached)
2. Reply to confirm your participation
3. I'll send you download links and access instructions

BETA TESTER AGREEMENT:
Please review the attached BETA-TESTER-AGREEMENT.md

Looking forward to your feedback!

Best regards,
[Your Name]
Fragillidae Software
```

### Track Your Testers

Create a simple spreadsheet:

| Name | Email | Platform | Accepted Agreement | Download Date | Last Feedback |
|------|-------|----------|-------------------|---------------|---------------|
| John Doe | john@example.com | Windows | 2026-02-14 | 2026-02-14 | 2026-02-15 |
| Jane Smith | jane@example.com | macOS | 2026-02-14 | 2026-02-15 | - |

---

## Step 5: Provide Access

### For GitHub Private Repo

1. GitHub → Settings → Collaborators
2. Add tester's GitHub username
3. Set permission to **"Read"** (they can download releases but NOT see code)
4. They'll receive an invitation email

### For Other Methods

Send them:
- Download link
- Password (if applicable)
- INSTALLATION.md
- BETA-TESTER-AGREEMENT.md

---

## Step 6: Collect Feedback

### Set Up Feedback Channels

**Option 1: GitHub Issues (Private Repo)**
- Testers can file issues
- You can track and manage bugs
- Organized and searchable

**Option 2: Email**
- Simple and direct
- Good for small groups
- Harder to track

**Option 3: Google Form**
- Structured feedback
- Easy to analyze
- Can include satisfaction ratings

### Create Feedback Template

```markdown
## Bug Report Template

**Platform:** (Windows/Mac/Linux)
**Version:** 1.0.0-beta1

**Description:**
[What happened?]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**
[What should have happened?]

**Actual Behavior:**
[What actually happened?]

**Screenshots:**
[If applicable]
```

---

## Step 7: Iterate

1. **Collect feedback** for 1-2 weeks
2. **Fix critical bugs**
3. **Build new release** (v1.0.0-beta2)
4. **Notify testers** of the update
5. **Repeat**

---

## Monetization Considerations

While running your beta, think about:

### Potential Business Models

1. **Freemium**
   - Free interpreter
   - Paid IDE with advanced features
   - Example: VS Code (free) vs. JetBrains (paid)

2. **Educational Licensing**
   - Free for students/educators
   - Paid for commercial use
   - Example: GitHub Student Pack model

3. **Subscription**
   - Monthly/yearly subscription
   - Includes updates and support
   - Example: JetBrains model

4. **One-Time Purchase**
   - Pay once, use forever
   - Paid upgrades for major versions
   - Example: Sublime Text model

5. **Dual License**
   - Free for open source projects
   - Paid for commercial/proprietary use
   - Example: Qt model

6. **Support & Training**
   - Free software
   - Paid support contracts
   - Paid training courses

### Questions to Ask Beta Testers

- Would you pay for this? How much?
- What features would justify a paid version?
- Would your school/company pay for licenses?
- Would you prefer subscription or one-time purchase?

---

## Legal Protection

### Minimum Protection (What You Have Now)

✅ Beta Tester Agreement (created above)
✅ Copyright notice in LICENSE file
✅ Private distribution

### Additional Protection (Optional)

- **Trademark:** Register "PLAIN" as a trademark (~$250-500)
- **Copyright Registration:** Register with US Copyright Office (~$65)
- **Patent:** If you have novel language features (expensive, $5k-15k)
- **Lawyer Review:** Have a lawyer review your agreements (~$500-1000)

**For now, the Beta Tester Agreement is sufficient for a small private beta.**

---

## Sample Release Notes

```markdown
# PLAIN v1.0.0-beta1 - Private Beta Release

**⚠️ CONFIDENTIAL - Beta Testers Only**

This is a private beta release. Please do not share this software.

## What's New

- Initial release of PLAIN interpreter
- Full-featured IDE with syntax highlighting
- 93+ built-in functions
- Complete documentation and tutorial
- 20+ example programs

## Known Issues

- [List any known bugs]

## Installation

See INSTALLATION.md for detailed setup instructions.

## Feedback

Please report bugs and feedback via:
- GitHub Issues: [private repo URL]
- Email: info@fragillidaesoftware.com

## Thank You!

Thank you for participating in the PLAIN beta program. Your feedback 
is invaluable in making PLAIN better.

---

**Remember:** This software is confidential. Please do not share.
```

---

## Checklist

- [ ] Make GitHub repo private
- [ ] Build releases on all platforms
- [ ] Create GitHub release (or upload to hosting)
- [ ] Prepare Beta Tester Agreement
- [ ] Create invitation email
- [ ] Identify 5-10 initial testers
- [ ] Send invitations
- [ ] Provide access to downloads
- [ ] Set up feedback channel
- [ ] Monitor feedback
- [ ] Plan next iteration

---

## Timeline Suggestion

**Week 1:** Invite 5-10 testers, get initial feedback
**Week 2:** Fix critical bugs, release beta2
**Week 3:** Expand to 20-30 testers
**Week 4:** Collect monetization feedback
**Week 5-6:** Decide on business model
**Week 7-8:** Prepare for public launch (if desired)

---

**You're ready to start your private beta!** 🚀

Remember: Start small (5-10 testers), iterate quickly, and gather feedback 
before deciding on monetization.

