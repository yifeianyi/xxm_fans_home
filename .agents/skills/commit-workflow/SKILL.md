---
name: commit-workflow
description: Standardize Git commit workflow for main repository and sub-repositories with task management support
---

This skill provides comprehensive guidance for Git commit workflows in the XXM Fans Home project, covering both the main repository and all sub-repositories (submodules).

## Overview

The XXM Fans Home project uses a **multi-repository architecture**:
- **Main repository**: `xxm_fans_home` (this project root)
- **Sub-repositories** (submodules):
  - `repo/xxm_fans_backend` - Django backend
  - `repo/xxm_fans_frontend` - React frontend
  - `repo/TempSongListFrontend` - Vue songlist frontend

### Repository Status Types

| Status | Description | Workflow |
|--------|-------------|----------|
| **Linked** | Already added as git submodule | Commit to sub-repo → Update main repo reference |
| **Standalone** | Independent git repository (not yet linked) | Commit directly to sub-repo |
| **Main Only** | Main repository changes | Commit directly to main repo |

## Usage

When asked to commit changes or manage Git workflow:

1. **Identify target repository** - Determine which repo(s) have changes
2. **Check repository status** - Linked, Standalone, or Main Only
3. **Apply commit standards** - Follow Conventional Commits format
4. **Handle cross-repo dependencies** - Update submodules in main repo if needed

## Quick Start

### 1. Determine Repository Structure

```bash
# Check if we're in a submodule
cd repo/xxm_fans_backend
git remote -v

# Check if submodule is properly linked
cd /home/yifeianyi/Desktop/xxm_fans_home
git submodule status

# Check for uncommitted changes
git status                    # Main repo
git -C repo/xxm_fans_backend status   # Sub-repo
```

### 2. Commit Based on Repository Type

```bash
# Type A: Standalone sub-repo (not yet linked)
cd repo/xxm_fans_backend
git add -A
git commit -m "feat: add new API endpoint"
git push origin main

# Type B: Linked sub-repo (already a submodule)
cd repo/xxm_fans_backend
git add -A
git commit -m "feat: add new API endpoint"
git push origin main
# Then update main repo reference (see below)

# Type C: Main repo only
cd /home/yifeianyi/Desktop/xxm_fans_home
git add -A
git commit -m "docs: update deployment guide"
git push origin main
```

### 3. Update Submodule Reference (for Linked repos)

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# Stage submodule changes
git add repo/xxm_fans_backend

# Commit with descriptive message
git commit -m "chore: update backend submodule

- Add new API endpoint for song search
- Fix authentication bug"

git push origin main
```

## Available Modules

1. **[Main Repository Guide](./main-repo.md)** - Main repository workflow
   - Status: Root project management
   - Purpose: Handle main repo changes and submodule coordination

2. **[Backend Repository Guide](./backend-repo.md)** - Django backend workflow
   - Status: Can be Linked or Standalone
   - Purpose: Backend API development commits

3. **[Frontend Repository Guide](./frontend-repo.md)** - React frontend workflow
   - Status: Can be Linked or Standalone
   - Purpose: Frontend UI development commits

4. **[Songlist Repository Guide](./songlist-repo.md)** - Vue songlist workflow
   - Status: Can be Linked or Standalone
   - Purpose: Songlist template development commits

5. **[Next.js Migration Repository Guide](./nextjs-repo.md)** - Next.js migration workflow
   - Status: Standalone (local development, no remote)
   - Purpose: Next.js migration development commits
   - Special: Will be merged into frontend repo when complete

## Common Standards (All Repositories)

### Commit Message Format (Conventional Commits)

```
<type>(<scope>): <subject>

<body> (optional)

<footer> (optional)
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add user authentication` |
| `fix` | Bug fix | `fix: resolve login timeout issue` |
| `docs` | Documentation | `docs: update API documentation` |
| `style` | Code style | `style: fix indentation` |
| `refactor` | Code refactoring | `refactor: simplify data processing` |
| `perf` | Performance | `perf: optimize database query` |
| `test` | Tests | `test: add unit tests for login` |
| `chore` | Maintenance | `chore: update dependencies` |
| `ci` | CI/CD | `ci: update GitHub Actions` |
| `build` | Build system | `build: update webpack config` |

### Scopes by Repository

**Main Repository (`xxm_fans_home`)**:
- `infra` - Infrastructure (nginx, systemd)
- `scripts` - Utility scripts
- `docs` - Documentation
- `config` - Configuration files
- `submodule` - Submodule updates

**Backend (`xxm_fans_backend`)**:
- `api` - API endpoints
- `model` - Database models
- `admin` - Django admin
- `service` - Business logic
- `spider` - Crawler scripts

**Frontend (`xxm_fans_frontend`)**:
- `component` - React components
- `page` - Page components
- `hook` - Custom hooks
- `api` - API services
- `style` - Styling/Tailwind

**Songlist (`TempSongListFrontend`)**:
- `component` - Vue components
- `view` - Page views
- `store` - State management

### Subject Guidelines

- Use imperative mood ("add" not "added")
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

✅ **Good**:
```
feat(api): add song search endpoint
fix(auth): resolve token expiration bug
docs(readme): update installation guide
```

❌ **Bad**:
```
feat(api): Added song search endpoint.      # Past tense + period
feat: update                                # Too vague
fix: bug fix                                # Redundant
```

## Task Management Workflow

### Creating a New Task

```bash
# 1. Create feature branch (recommended for large tasks)
git checkout -b feat/song-search-api

# 2. Make changes and commit
git add -A
git commit -m "feat(api): implement song search endpoint

- Add search by title, artist, style
- Support pagination
- Add search result caching"

# 3. Complete task and merge
git checkout main
git merge feat/song-search-api
git push origin main
```

### Multi-Repository Task Coordination

When a task spans multiple repositories:

```bash
# Task: Add new song feature (requires both backend and frontend)

# Step 1: Backend changes
cd repo/xxm_fans_backend
git checkout -b feat/new-song-feature
git add -A
git commit -m "feat(api): add new song creation endpoint"
git push origin feat/new-song-feature
# Create PR and merge...

# Step 2: Frontend changes
cd repo/xxm_fans_frontend
git checkout -b feat/new-song-ui
git add -A
git commit -m "feat(page): add song creation form"
git push origin feat/new-song-ui
# Create PR and merge...

# Step 3: Update main repo (if submodules are linked)
cd /home/yifeianyi/Desktop/xxm_fans_home
git add repo/xxm_fans_backend repo/xxm_fans_frontend
git commit -m "chore(submodule): update for new song feature

Backend:
- Add song creation API endpoint

Frontend:
- Add song creation form UI"
git push origin main
```

## Quick Reference

### When working with Main Repository
→ Read [main-repo.md](./main-repo.md)

### When working with Backend (Django)
→ Read [backend-repo.md](./backend-repo.md)

### When working with Frontend (React)
→ Read [frontend-repo.md](./frontend-repo.md)

### When working with Songlist (Vue)
→ Read [songlist-repo.md](./songlist-repo.md)

### When working with Next.js Migration
→ Read [nextjs-repo.md](./nextjs-repo.md)

## Key Principles

1. **Atomic Commits** - Each commit should represent a single logical change
2. **Clear Messages** - Use Conventional Commits for clarity and automation
3. **Repository Separation** - Keep sub-repo changes separate from main repo changes
4. **Submodule Updates** - Always commit sub-repo changes before updating main repo reference
5. **Task Tracking** - Use descriptive branch names for multi-commit tasks

## Common Issues

### Issue: "Changes in submodule but main repo shows modified"

**Cause**: Sub-repo has uncommitted changes

**Solution**:
```bash
cd repo/xxm_fans_backend
git add -A
git commit -m "feat: your changes"
git push origin main

cd /home/yifeianyi/Desktop/xxm_fans_home
git add repo/xxm_fans_backend
git commit -m "chore(submodule): update backend"
```

### Issue: "Detached HEAD in submodule"

**Cause**: Submodule is not on a branch

**Solution**:
```bash
cd repo/xxm_fans_backend
git checkout main
git pull origin main
```

### Issue: "Cannot push to submodule"

**Cause**: Standalone repo not configured with remote

**Solution**:
```bash
cd repo/xxm_fans_backend
git remote -v  # Check remotes
git remote add origin <url>  # If missing
git push -u origin main
```
