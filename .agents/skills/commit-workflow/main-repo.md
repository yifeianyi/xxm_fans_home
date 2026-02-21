# Main Repository Commit Guide

## Module Overview

**Purpose**: Manage commits for the main `xxm_fans_home` repository

**Scope**: Infrastructure, scripts, documentation, and submodule coordination

**Location**: `/home/yifeianyi/Desktop/xxm_fans_home`

---

## Repository Structure

```
xxm_fans_home/
├── .agents/              # AI Agent skills
├── data/                 # Data files
├── doc/                  # Documentation
├── env/                  # Environment configs
├── infra/                # Infrastructure (nginx, systemd)
├── media/                # Media files
├── repo/                 # Sub-repositories (submodules)
│   ├── xxm_fans_backend/
│   ├── xxm_fans_frontend/
│   └── TempSongListFrontend/
├── scripts/              # Utility scripts
└── spider/               # Crawler scripts
```

---

## Commit Categories

### 1. Infrastructure Changes (`infra/*`)

**Files**: `infra/nginx/*`, `infra/systemd/*`, `infra/gunicorn/*`

```bash
# Nginx configuration update
git add infra/nginx/
git commit -m "infra(nginx): add rate limiting for API endpoints

- Limit requests to 100/minute per IP
- Add burst handling for legitimate traffic"

# Systemd service update
git add infra/systemd/
git commit -m "infra(systemd): add health check to crawler service

- Restart service on failure
- Add 30s timeout"
```

### 2. Script Changes (`scripts/*`)

**Files**: `scripts/*.sh`, `scripts/*.py`

```bash
# New deployment script
git add scripts/deploy.sh
git commit -m "feat(scripts): add automated deployment script

- Support staging and production environments
- Include rollback capability
- Add pre-deployment checks"

# Update existing script
git add scripts/dev_start_services.sh
git commit -m "fix(scripts): resolve port conflict in dev startup

- Check port availability before starting
- Auto-select alternative ports if occupied"
```

### 3. Documentation Changes (`doc/*`, `*.md`)

**Files**: `doc/**/*.md`, `*.md`, `README.md`

```bash
# Architecture documentation
git add doc/architecture/nextjs-migration-todo.md
git commit -m "docs(architecture): add Next.js migration todo

- Include 6-phase migration plan
- Add testing and acceptance criteria"

# README update
git commit -m "docs(readme): update installation instructions

- Update system requirements
- Add local deployment guide"
```

### 4. Configuration Changes (`env/*`, `*.conf`)

**Files**: `env/*.env`, `*.conf`

```bash
# Environment configuration
git add env/backend.env
git commit -m "config(env): add Spotify API credentials

- Add SPOTIPY_CLIENT_ID
- Add SPOTIPY_CLIENT_SECRET"
```

### 5. Submodule Coordination (`repo/*`)

**When to use**: After committing changes to sub-repositories

```bash
# Update single submodule
git add repo/xxm_fans_backend
git commit -m "chore(submodule): update backend to v2.1.0

- Add new song search API
- Fix authentication issues"

# Update multiple submodules
git add repo/xxm_fans_backend repo/xxm_fans_frontend
git commit -m "chore(submodule): update for new gallery feature

Backend:
- Add gallery image upload API
- Add thumbnail generation

Frontend:
- Add gallery upload UI
- Implement image preview"
```

---

## Special Commit Types

### Multi-Submodule Updates

When coordinating changes across multiple submodules:

```bash
# Step 1: Update each submodule individually
cd repo/xxm_fans_backend
git add -A
git commit -m "feat(api): add export functionality"
git push origin main

cd repo/xxm_fans_frontend
git add -A
git commit -m "feat(page): add export button"
git push origin main

# Step 2: Update main repo with clear description
cd /home/yifeianyi/Desktop/xxm_fans_home
git add repo/xxm_fans_backend repo/xxm_fans_frontend
git commit -m "chore(submodule): add data export feature

Backend (xxm_fans_backend):
- Add /api/export/songs endpoint
- Support CSV and JSON formats
- Add export progress tracking

Frontend (xxm_fans_frontend):
- Add export button to song list
- Implement export format selection
- Add download progress indicator

Related: #123"
```

### Next.js Migration Commits

Special workflow for the Next.js migration project:

```bash
# Phase 1: Environment setup
git add scripts/dev_start_nextjs.sh scripts/dev_stop_nextjs.sh
git commit -m "feat(scripts): add Next.js development environment scripts

- dev_start_nextjs.sh: Start Next.js dev server with backend
- dev_stop_nextjs.sh: Stop Next.js development environment"

# Phase completion tag
git tag -a v0.1.0-init -m "Phase 1: Environment setup complete"
```

---

## Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Allowed Scopes

| Scope | Description | Example |
|-------|-------------|---------|
| `infra` | Infrastructure config | `infra(nginx)`, `infra(systemd)` |
| `scripts` | Utility scripts | `scripts(deploy)`, `scripts(backup)` |
| `docs` | Documentation | `docs(readme)`, `docs(architecture)` |
| `config` | Configuration | `config(env)`, `config(nginx)` |
| `submodule` | Submodule updates | `submodule(backend)`, `submodule(all)` |
| `skills` | AI Agent skills | `skills(commit)`, `skills(module)` |

### Subject Rules

- Use imperative mood ("add" not "added")
- No period at the end
- Maximum 50 characters
- Be specific about what changed

### Body Rules

- Separate from subject with blank line
- Wrap at 72 characters
- Explain **what** and **why**, not **how**
- Use bullet points for multiple changes

---

## Verification Checklist

Before committing to main repo:

- [ ] Changes are limited to main repo files (not sub-repo code)
- [ ] If updating submodules, sub-repo changes are already committed
- [ ] Commit message follows format: `type(scope): subject`
- [ ] Subject is descriptive and < 50 characters
- [ ] Body explains what and why (if needed)
- [ ] No sensitive data in commit (passwords, keys)

---

## Common Commands

```bash
# Check repository status
git status

# View changes in submodules
git diff --submodule

# Update all submodules
git submodule update --init --recursive

# Check submodule commits
git submodule status

# Stage submodule changes
git add repo/xxm_fans_backend

# Commit with detailed message
git commit -m "chore(submodule): update backend

- Add feature X
- Fix bug Y"

# Push to remote
git push origin main
```
