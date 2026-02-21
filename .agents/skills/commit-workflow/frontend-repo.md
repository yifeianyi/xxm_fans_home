# Frontend Repository (React) Commit Guide

## Module Overview

**Purpose**: Manage commits for the React frontend repository

**Location**: `repo/xxm_fans_frontend/` (can be standalone or linked submodule)

**Status**: May be **Linked** (submodule) or **Standalone** (independent)

**Current Stack**: React 19 + Vite + TypeScript + Tailwind CSS + SWR

---

## Repository Structure

```
xxm_fans_frontend/
├── src/
│   ├── domain/           # Domain layer (types, interfaces)
│   ├── infrastructure/   # Infrastructure layer (API, config)
│   ├── presentation/     # Presentation layer (components, pages)
│   └── shared/           # Shared layer (utils, hooks)
├── public/               # Static assets
├── index.html
├── vite.config.ts
└── package.json
```

---

## Checking Repository Status

```bash
cd repo/xxm_fans_frontend

# Check if it's a standalone repo or submodule
git rev-parse --show-toplevel

# Check remote configuration
git remote -v

# Check current branch
git branch -v
```

---

## Commit Categories by Layer

### 1. Domain Layer (`src/domain/*`)

**Types, interfaces, and domain models**

```bash
# Add new type
git add src/domain/types.ts
git commit -m "feat(types): add Livestream type definition

- Define Livestream interface
- Add LivestreamSegment type
- Update related types"

# Interface update
git add src/domain/api/
git commit -m "feat(api): add gallery service interface

- Define IGalleryService
- Add method signatures for CRUD operations"
```

### 2. Infrastructure Layer (`src/infrastructure/*`)

**API services, configuration, data fetching**

```bash
# API service implementation
git add src/infrastructure/api/
git commit -m "feat(api): implement song service

- Add getSongs method
- Add search and filter support
- Implement error handling"

# Hook creation
git add src/infrastructure/hooks/
git commit -m "feat(hook): add useSongData hook

- Fetch song list with SWR
- Support pagination
- Add loading and error states"

# Configuration
git add src/infrastructure/config/
git commit -m "config(routes): add new gallery routes

- Add /gallery route
- Add /gallery/:id route"
```

### 3. Presentation Layer (`src/presentation/*`)

**Components and pages**

```bash
# Component creation
git add src/presentation/components/
git commit -m "feat(component): add SongCard component

- Display song info with cover
- Add hover effects
- Support click to play"

# Page creation
git add src/presentation/pages/
git commit -m "feat(page): add GalleryPage

- Display gallery grid
- Implement lazy loading
- Add image modal"

# Feature component
git add src/presentation/components/features/
git commit -m "feat(feature): add SongFilter component

- Filter by style, language
- Search by name
- Clear filters button"
```

### 4. Shared Layer (`src/shared/*`)

**Utilities and shared hooks**

```bash
# Utility function
git add src/shared/utils/
git commit -m "feat(utils): add date formatting utilities

- Format to relative time (e.g., '2 days ago')
- Format to custom pattern
- Handle timezone"

# Shared hook
git add src/shared/hooks/
git commit -m "feat(hook): add useInfiniteScroll hook

- Trigger callback on scroll to bottom
- Support loading state
- Add threshold configuration"
```

---

## Special Scenarios

### Next.js Migration Commits

For the Next.js migration project:

```bash
# Phase 1: Initial setup
git add package.json next.config.ts
git commit -m "feat(config): initialize Next.js project

- Add Next.js 15.1.x
- Configure TypeScript
- Setup Tailwind CSS 4"

# Phase 2: Type migration
git add app/domain/
git commit -m "feat(types): migrate domain types to Next.js

- Move types to app/domain/types.ts
- Update import paths"

# Phase 3: Page migration
git add app/songs/page.tsx
git commit -m "feat(page): migrate songs page to Next.js

- Convert to Server Component
- Add ISR configuration
- Implement search and filter"

# Phase completion
git tag -a v0.4.0-data-pages -m "Phase 4: Data-driven pages migration complete"
```

### Component Refactoring

```bash
# Breaking change refactoring
git add src/presentation/components/
git commit -m "refactor(component): simplify SongTable props

BREAKING CHANGE: SongTable props changed

Before:
  <SongTable songs={songs} columns={columns} onSort={onSort} />

After:
  <SongTable data={songs} sortable onRowClick={handleClick} />

Migration:
- Replace 'songs' with 'data'
- Remove 'columns' prop (auto-detected)
- Use 'sortable' boolean instead of onSort"
```

### Style Changes

```bash
# Tailwind customization
git add src/styles/ tailwind.config.ts
git commit -m "style(theme): add custom color palette

- Add sage green: #9caf88
- Add peach accent: #f8b195
- Update button variants"

# Responsive design
git add src/presentation/components/
git commit -m "style(responsive): improve mobile layout

- Stack filters on mobile
- Adjust grid columns
- Hide sidebar on small screens"
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
| `component` | React components | `component(button)`, `component(modal)` |
| `page` | Page components | `page(songs)`, `page(gallery)` |
| `hook` | Custom hooks | `hook(useData)`, `hook(useAuth)` |
| `api` | API services | `api(song)`, `api(gallery)` |
| `types` | Type definitions | `types(song)`, `types(api)` |
| `utils` | Utility functions | `utils(date)`, `utils(format)` |
| `config` | Configuration | `config(vite)`, `config(ts)` |
| `style` | Styling changes | `style(tailwind)`, `style(css)` |
| `test` | Tests | `test(component)`, `test(hook)` |

### Subject Rules

- Use present tense, imperative mood
- Maximum 50 characters
- No period at the end
- Be specific about the change

### Body Rules

- Separate from subject with blank line
- Wrap at 72 characters
- Explain motivation
- Document breaking changes

---

## Workflow for Standalone Repo

When frontend is not yet linked as submodule:

```bash
# 1. Navigate to frontend repo
cd repo/xxm_fans_frontend

# 2. Create feature branch
git checkout -b feat/gallery-redesign

# 3. Make changes
# ... edit files ...

# 4. Stage and commit
git add -A
git commit -m "feat(page): redesign gallery page

- New masonry layout
- Improved image loading
- Add lightbox"

# 5. Type check
npx tsc --noEmit

# 6. Build test
npm run build

# 7. Push and merge
git push origin feat/gallery-redesign
# Create PR, review, merge...
```

---

## Verification Checklist

Before committing:

- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors
- [ ] Code follows project style
- [ ] Components have proper types
- [ ] Commit message follows format
- [ ] Related issue referenced (if applicable)

---

## Common Commands

```bash
# Type checking
npx tsc --noEmit

# Build
npm run build

# Development
npm run dev

# Lint
npm run lint

# Git workflow
git status
git add -A
git commit -m "type(scope): description"
git push origin main
```
