# Backend Repository (Django) Commit Guide

## Module Overview

**Purpose**: Manage commits for the Django backend repository

**Location**: `repo/xxm_fans_backend/` (can be standalone or linked submodule)

**Status**: May be **Linked** (submodule) or **Standalone** (independent)

---

## Repository Structure

```
xxm_fans_backend/
├── song_management/      # Song and performance records
├── fansDIY/              # Fan-created content
├── site_settings/        # Website configuration
├── data_analytics/       # Data analysis and metrics
├── gallery/              # Photo gallery management
├── livestream/           # Live stream records
├── songlist/             # Template-based song lists
├── core/                 # Shared utilities
├── tools/                # Management tools
└── spider/               # Bilibili crawler tools
```

---

## Checking Repository Status

```bash
cd repo/xxm_fans_backend

# Check if it's a standalone repo or submodule
git rev-parse --show-toplevel
# If output is /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
# → Standalone or properly linked submodule

# Check remote configuration
git remote -v

# Check current branch
git branch -v
```

---

## Commit Categories by App

### 1. Song Management (`song_management/*`)

**Models**: Song, SongRecord, Style, Tag

```bash
# New model field
git add song_management/models/song.py
git commit -m "feat(model): add duration field to Song model

- Store song duration in seconds
- Add duration formatting method
- Update admin display"

# API endpoint
git add song_management/api/
git commit -m "feat(api): add bulk import endpoint for songs

- Support CSV import
- Validate required fields
- Return import summary"

# Admin customization
git add song_management/admin/
git commit -m "feat(admin): add export action to Song admin

- Export selected songs to CSV
- Include all metadata fields"
```

### 2. Fan DIY (`fansDIY/*`)

**Models**: Collection, Work

```bash
# Model changes
git add fansDIY/models/
git commit -m "feat(model): add Work thumbnail field

- Auto-generate thumbnail on save
- Support custom thumbnail upload"

# Admin features
git add fansDIY/admin.py
git commit -m "feat(admin): add BV import for Works

- Import work details from Bilibili
- Auto-fetch cover image"
```

### 3. Data Analytics (`data_analytics/*`)

**Models**: WorkStatic, WorkMetricsHour, CrawlSession

```bash
# New metrics
git add data_analytics/models.py
git commit -m "feat(model): add hourly follower tracking

- Track follower count per hour
- Calculate growth rate"

# Spider improvements
git add data_analytics/spider/
git commit -m "perf(spider): optimize tiered crawler performance

- Add hot/cold data separation
- Implement batch updates"
```

### 4. Gallery (`gallery/*`)

**Models**: Gallery, GalleryItem

```bash
# Feature addition
git add gallery/
git commit -m "feat(api): add bulk upload for gallery images

- Support multiple file upload
- Auto-generate thumbnails
- Add upload progress tracking"
```

### 5. Livestream (`livestream/*`)

**Models**: Livestream

```bash
# Calendar feature
git add livestream/
git commit -m "feat(api): add calendar data endpoint

- Return monthly livestream summary
- Support date range filtering"
```

### 6. Core & Tools (`core/*`, `tools/*`)

```bash
# Utility improvement
git add core/thumbnail_generator.py
git commit -m "perf(core): optimize thumbnail generation

- Use Pillow-SIMD for faster processing
- Add WebP format support"

# Management command
git add tools/import_song_records.py
git commit -m "feat(tools): add song record import script

- Import from JSON/CSV
- Validate song existence
- Log import errors"
```

---

## Special Scenarios

### Database Migrations

Always include migrations in the same commit as model changes:

```bash
# Make model changes
# ... edit models ...

# Generate migrations
python manage.py makemigrations

# Commit together
git add song_management/models/ song_management/migrations/
git commit -m "feat(model): add Song status field

- Add status: active, archived, draft
- Default to active for existing records

Migration: 0008_add_song_status"
```

### API Changes

Document breaking changes in commit body:

```bash
git add song_management/api/
git commit -m "feat(api): redesign song search endpoint

BREAKING CHANGE: Search endpoint response format changed

Old:
  { "results": [...], "count": 100 }

New:
  { "data": [...], "meta": { "total": 100, "page": 1 } }

Migration guide:
- Update frontend to use 'data' instead of 'results'
- Read total from 'meta.total' instead of 'count'"
```

### Spider/Crawler Changes

```bash
# Spider improvement
git add spider/bilibili_crawler.py
git commit -m "fix(spider): handle rate limiting from Bilibili

- Add exponential backoff
- Implement request throttling
- Add user-agent rotation

Fixes #456"
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
| `model` | Database models | `model(song)`, `model(user)` |
| `api` | API endpoints | `api(songs)`, `api(auth)` |
| `admin` | Django admin | `admin(song)`, `admin(site)` |
| `service` | Business logic | `service(search)`, `service(export)` |
| `spider` | Crawler scripts | `spider(bilibili)`, `spider(weibo)` |
| `tool` | Management tools | `tool(import)`, `tool(backup)` |
| `core` | Shared utilities | `core(cache)`, `core(response)` |
| `test` | Tests | `test(api)`, `test(model)` |
| `mig` | Migrations only | `mig(song_management)` |

### Subject Rules

- Use present tense, imperative mood
- Maximum 50 characters
- No period at the end
- Be specific about the change

### Body Rules

- Separate from subject with blank line
- Wrap at 72 characters
- Explain motivation and contrast with previous behavior
- Reference issues: `Fixes #123`, `Related #456`

### Footer Rules

- Reference GitHub issues
- Mark breaking changes: `BREAKING CHANGE: description`

---

## Workflow for Standalone Repo

When backend is not yet linked as submodule:

```bash
# 1. Navigate to backend repo
cd repo/xxm_fans_backend

# 2. Create feature branch (optional)
git checkout -b feat/new-feature

# 3. Make changes
# ... edit files ...

# 4. Stage and commit
git add -A
git commit -m "feat(api): add new feature

- Description of changes"

# 5. Push to remote
git push origin feat/new-feature

# 6. Create PR or merge
git checkout main
git merge feat/new-feature
git push origin main

# 7. Later: Update main repo submodule reference
# (when backend becomes a linked submodule)
cd /home/yifeianyi/Desktop/xxm_fans_home
git add repo/xxm_fans_backend
git commit -m "chore(submodule): update backend"
```

---

## Verification Checklist

Before committing:

- [ ] Code follows project style guide
- [ ] Tests pass: `python manage.py test`
- [ ] Migrations included (if model changed)
- [ ] No debug code or print statements
- [ ] Sensitive data not committed
- [ ] Commit message follows format
- [ ] Related issue referenced (if applicable)

---

## Common Commands

```bash
# Run tests
python manage.py test

# Check migrations
python manage.py showmigrations

# Generate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check code style
flake8 .

# Run type checker
mypy .

# Git workflow
git status
git add -A
git commit -m "type(scope): description"
git push origin main
```
