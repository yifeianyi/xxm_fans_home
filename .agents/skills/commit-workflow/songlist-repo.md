# Songlist Repository (Vue) Commit Guide

## Module Overview

**Purpose**: Manage commits for the Vue-based songlist template repository

**Location**: `repo/TempSongListFrontend/` (can be standalone or linked submodule)

**Status**: May be **Linked** (submodule) or **Standalone** (independent)

**Current Stack**: Vue 3.2 + Element Plus 2.0 + Vite 4.0

---

## Repository Structure

```
TempSongListFrontend/
├── src/
│   ├── components/       # Vue components
│   ├── views/            # Page views
│   ├── stores/           # Pinia stores
│   ├── api/              # API services
│   ├── utils/            # Utilities
│   └── assets/           # Static assets
├── public/               # Public files
├── index.html
├── vite.config.js
└── package.json
```

---

## Checking Repository Status

```bash
cd repo/TempSongListFrontend

# Check if it's a standalone repo or submodule
git rev-parse --show-toplevel

# Check remote configuration
git remote -v

# Check current branch
git branch -v
```

---

## Commit Categories

### 1. Components (`src/components/*`)

**Reusable Vue components**

```bash
# Component creation
git add src/components/SongTable.vue
git commit -m "feat(component): add SongTable component

- Display song list with sorting
- Support pagination
- Add row selection"

# Component update
git add src/components/SearchBar.vue
git commit -m "feat(component): add advanced filters to SearchBar

- Add style filter dropdown
- Add language filter
- Add clear filters button"
```

### 2. Views (`src/views/*`)

**Page-level components**

```bash
# View creation
git add src/views/SongListView.vue
git commit -m "feat(view): add SongListView page

- Display paginated song list
- Add search and filters
- Implement responsive layout"

# Artist-specific feature
git add src/views/
git commit -m "feat(view): add artist switcher support

- Read artist from URL param
- Load artist-specific config
- Apply artist theme"
```

### 3. Stores (`src/stores/*`)

**Pinia state management**

```bash
# Store creation
git add src/stores/songStore.js
git commit -m "feat(store): add song store

- Manage song list state
- Add search and filter state
- Implement cache"

# Store update
git add src/stores/configStore.js
git commit -m "feat(store): add artist configuration store

- Load artist config from API
- Store theme settings
- Cache config data"
```

### 4. API (`src/api/*`)

**API service functions**

```bash
# API service
git add src/api/songApi.js
git commit -m "feat(api): add song API functions

- Add fetchSongs with pagination
- Add searchSongs
- Add getSongById"

# API update
git add src/api/configApi.js
git commit -m "feat(api): add artist config API

- Fetch artist settings
- Get available artists list"
```

### 5. Configuration & Assets

**Config files and static assets**

```bash
# Config update
git add vite.config.js
git commit -m "config(vite): update build configuration

- Add path aliases
- Optimize bundle size
- Update dev server port"

# Style update
git add src/assets/styles/
git commit -m "style(theme): add Element Plus theme customization

- Override primary color
- Customize table styles
- Add responsive breakpoints"
```

---

## Multi-Artist Support

The songlist frontend supports multiple artists through URL parameters:

```bash
# Artist-specific feature
git add src/views/ArtistView.vue
git commit -m "feat(view): implement artist-specific page layout

- Support artist=youyou parameter
- Support artist=bingjie parameter
- Apply artist-specific theme colors"

# Theme system
git add src/composables/useArtistTheme.js
git commit -m "feat(composable): add artist theme composable

- Load theme based on artist param
- Apply CSS variables dynamically
- Support custom artist configs"
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
| `component` | Vue components | `component(table)`, `component(modal)` |
| `view` | Page views | `view(list)`, `view(detail)` |
| `store` | Pinia stores | `store(song)`, `store(config)` |
| `api` | API services | `api(song)`, `api(config)` |
| `composable` | Vue composables | `composable(theme)`, `composable(fetch)` |
| `config` | Configuration | `config(vite)`, `config(eslint)` |
| `style` | Styling | `style(css)`, `style(theme)` |
| `utils` | Utilities | `utils(format)`, `utils(validate)` |
| `asset` | Static assets | `asset(icon)`, `asset(font)` |

### Subject Rules

- Use present tense, imperative mood
- Maximum 50 characters
- No period at the end
- Be specific about the change

### Body Rules

- Separate from subject with blank line
- Wrap at 72 characters
- Explain motivation and implementation details

---

## Workflow for Standalone Repo

When songlist is not yet linked as submodule:

```bash
# 1. Navigate to songlist repo
cd repo/TempSongListFrontend

# 2. Create feature branch
git checkout -b feat/new-artist-support

# 3. Make changes
# ... edit files ...

# 4. Stage and commit
git add -A
git commit -m "feat(config): add support for new artist

- Add artist configuration
- Implement artist-specific styling
- Update API endpoints"

# 5. Build test
npm run build

# 6. Push and merge
git push origin feat/new-artist-support
# Create PR, review, merge...
```

---

## Verification Checklist

Before committing:

- [ ] Build succeeds: `npm run build`
- [ ] No console errors
- [ ] ESLint passes: `npm run lint`
- [ ] Components properly typed (if using TypeScript)
- [ ] Commit message follows format
- [ ] Artist-specific changes tested with different artist params

---

## Common Commands

```bash
# Development
npm run dev          # http://localhost:5174

# Build
npm run build

# Preview production
npm run preview

# Lint
npm run lint

# Git workflow
git status
git add -A
git commit -m "type(scope): description"
git push origin main
```

---

## Testing Multi-Artist Support

```bash
# Start dev server
npm run dev

# Test different artists
open http://localhost:5174?artist=youyou
open http://localhost:5174?artist=bingjie

# Verify:
# - Different themes applied
# - Different song lists loaded
# - Artist name displayed correctly
```
