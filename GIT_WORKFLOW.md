# Git Workflow & Branch Protection Setup

## Branch Strategy (Git Flow)

### Branch Structure

1. **`main`** - Production/stable code only
   - Always deployable
   - Protected branch
   - Only merge from `develop` via pull requests

2. **`develop`** - Integration/testing branch
   - Your "test repo"
   - All features merge here first
   - Test thoroughly before merging to `main`

3. **`feature/*`** - Individual feature branches
   - Created from `develop`
   - One branch per feature
   - Example: `feature/add-reports`, `feature/fix-login`

## Typical Development Workflow

### Starting a New Feature

```bash
# 1. Switch to develop and get latest changes
git checkout develop
git pull origin develop

# 2. Create a new feature branch
git checkout -b feature/my-new-feature

# 3. Work on your feature, commit changes
git add .
git commit -m "Add new feature"

# 4. Push feature branch to GitHub
git push -u origin feature/my-new-feature
```

### Merging Feature to Develop

```bash
# 5. Create Pull Request on GitHub
# Go to: https://github.com/BakersfieldEsportsJon/KRCCheckin/pulls
# Click "New Pull Request"
# Select: base: develop <- compare: feature/my-new-feature
# Review and merge on GitHub

# 6. After merge, update your local develop
git checkout develop
git pull origin develop

# 7. Delete the feature branch (optional)
git branch -d feature/my-new-feature
git push origin --delete feature/my-new-feature
```

### Releasing to Production

```bash
# 1. Create Pull Request from develop to main
# Go to: https://github.com/BakersfieldEsportsJon/KRCCheckin/pulls
# Select: base: main <- compare: develop
# Review, test, and merge

# 2. Tag the release (on main branch)
git checkout main
git pull origin main
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Version Numbering

Use semantic versioning: `vMAJOR.MINOR.PATCH`

- **MAJOR** - Breaking changes (v2.0.0)
- **MINOR** - New features, backwards compatible (v1.1.0)
- **PATCH** - Bug fixes (v1.0.1)

Examples:
- `v1.0.0` - Initial release
- `v1.1.0` - Added new reports feature
- `v1.1.1` - Fixed login bug
- `v2.0.0` - Major refactor with breaking changes

## Common Git Commands

```bash
# View all branches
git branch -a

# Switch branches
git checkout branch-name

# Create and switch to new branch
git checkout -b feature/new-branch

# Check status
git status

# See commit history
git log --oneline --graph --all

# Pull latest changes
git pull origin develop

# Push current branch
git push origin branch-name

# Delete local branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all local changes
git checkout -- .
```

## Setting Up Branch Protection Rules on GitHub

### Instructions

1. **Go to your repository on GitHub:**
   - https://github.com/BakersfieldEsportsJon/KRCCheckin

2. **Access Settings:**
   - Click on **"Settings"** tab at the top of your repository

3. **Navigate to Branches:**
   - In the left sidebar, click **"Branches"** (under "Code and automation")
   - Direct link: https://github.com/BakersfieldEsportsJon/KRCCheckin/settings/branches

4. **Add Branch Protection Rule:**
   - Click **"Add branch protection rule"** or **"Add rule"**

5. **Configure Protection for `main` branch:**
   - **Branch name pattern:** `main`

   **Recommended settings:**
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: 1 (for solo work) or more (for teams)
     - ✅ Dismiss stale pull request approvals when new commits are pushed

   - ✅ **Require status checks to pass before merging** (if you have CI/CD tests)

   - ✅ **Require conversation resolution before merging**

   - ✅ **Require linear history** (keeps history clean)

   - ⚠️ **Include administrators** (optional - even admins must follow rules)

6. **Click "Create"** or **"Save changes"**

7. **Repeat for `develop` branch (optional but recommended):**
   - Same settings as main
   - Helps maintain quality in your testing branch

### What Branch Protection Does

- **Prevents direct pushes** - All changes must go through pull requests
- **Requires code review** - Changes must be approved before merging
- **Keeps production stable** - Only tested code reaches `main`
- **Provides audit trail** - All changes are documented in PRs

### Solo Development Tips

If working alone, you can:
- Skip "Require approvals" for faster workflow
- Still require pull requests for documentation
- Review your own PRs before merging
- Gives you a chance to review changes before production

## Current Repository Setup

- **Repository:** https://github.com/BakersfieldEsportsJon/KRCCheckin
- **Main Branch:** `main` (production)
- **Develop Branch:** `develop` (testing/integration)
- **Remote:** `origin` (HTTPS)

## Workflow Summary

```
feature/new-feature  →  develop  →  main (v1.0.0)
      (PR)              (PR)       (tag)
     [Test]           [Stage]    [Production]
```

1. Develop features in `feature/*` branches
2. Merge to `develop` for integration testing
3. Merge to `main` for production release
4. Tag releases with version numbers
5. Never commit directly to `main` (use PRs)
