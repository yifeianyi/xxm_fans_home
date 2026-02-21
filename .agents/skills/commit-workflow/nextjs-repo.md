# Next.js Migration Repository Commit Guide

## Module Overview

**Purpose**: Manage commits for the Next.js migration development repository

**Location**: `repo/xxm_nextjs/` (local development only, no remote)

**Status**: **Standalone** (local development, will be merged into main repo later)

**Stack**: Next.js 15 + React 19 + TypeScript + Tailwind CSS

---

## Repository Characteristics

Unlike other sub-repositories, `xxm_nextjs` has special characteristics:

| Aspect | Description |
|--------|-------------|
| **Location** | `repo/xxm_nextjs/` (inside main project) |
| **Remote** | None (local development only) |
| **Lifecycle** | Temporary (will be merged into main repo) |
| **Commit Strategy** | Frequent small commits during development |
| **Final State** | Merged into `repo/xxm_fans_frontend` via Git orphan branch |

---

## Directory Structure

```
xxm_nextjs/
├── app/                  # Next.js App Router
│   ├── domain/           # Domain layer (types)
│   ├── infrastructure/   # Infrastructure layer
│   ├── components/       # React components
│   └── (routes)/         # Page routes
├── public/               # Static assets
├── next.config.ts        # Next.js config
├── tailwind.config.ts    # Tailwind config
├── tsconfig.json         # TypeScript config
└── package.json          # Dependencies
```

---

## Commit Workflow

### Phase-Based Commits

Organize commits by migration phase:

```bash
# Phase 1: Environment setup
git add -A
git commit -m "init: initialize Next.js 15 project

- Add Next.js with TypeScript
- Configure Tailwind CSS 4
- Add development scripts"
git tag v0.1.0-init

# Phase 2: Foundation
git add -A
git commit -m "feat(architecture): migrate DDD architecture

- Add domain types
- Create API services
- Setup global layout"
git tag v0.2.0-foundation

# Phase 3: Static pages
git add -A
git commit -m "feat(pages): add static pages

- Home page with ISR
- About page (SSG)
- Contact page (SSG)"
git tag v0.3.0-static-pages
```

### Feature-Based Commits

For incremental development within phases:

```bash
# Add a specific feature
git add app/songs/page.tsx
git commit -m "feat(page): add songs list page

- Server Component with SSR
- Add search and filter
- Implement pagination"

# Fix an issue
git add app/components/SongCard.tsx
git commit -m "fix(component): resolve image loading in SongCard

- Add error boundary
- Use next/image properly
- Add fallback image"

# Refactor
git add app/infrastructure/api/
git commit -m "refactor(api): simplify API error handling

- Centralize error handling
- Add consistent error messages
- Improve type safety"
```

---

## Commit Categories

### 1. Configuration (`config/*`)

```bash
# Next.js config
git add next.config.ts
git commit -m "config(next): add image domain whitelist

- Add bilibili.com domains
- Configure standalone output
- Add typed routes"

# TypeScript config
git add tsconfig.json
git commit -m "config(ts): update path aliases

- Add @/domain alias
- Add @/components alias
- Enable strict mode"

# Tailwind config
git add tailwind.config.ts
git commit -m "config(tailwind): migrate custom theme

- Add sage green color
- Add peach accent
- Configure custom fonts"
```

### 2. Domain Layer (`app/domain/*`)

```bash
# Type definitions
git add app/domain/types.ts
git commit -m "feat(types): add Song and SongRecord types

- Define Song interface
- Define SongRecord interface
- Add related enums"

# API interfaces
git add app/domain/api/
git commit -m "feat(api): add service interfaces

- Define ISongService
- Define IGalleryService
- Add response types"
```

### 3. Infrastructure Layer (`app/infrastructure/*`)

```bash
# API services
git add app/infrastructure/api/
git commit -m "feat(api): implement song service

- Add getSongs method
- Add search functionality
- Implement caching"

# Hooks
git add app/infrastructure/hooks/
git commit -m "feat(hook): add useSongs hook

- SWR integration
- Pagination support
- Error handling"
```

### 4. Components (`app/components/*`)

```bash
# Common components
git add app/components/common/
git commit -m "feat(component): add Loading and ErrorBoundary

- Add Loading spinner
- Add ErrorBoundary wrapper
- Add common animations"

# Feature components
git add app/components/features/
git commit -m "feat(component): add SongTable and SongCard

- Implement responsive table
- Add card grid layout
- Add hover effects"
```

### 5. Pages (`app/(routes)/*`)

```bash
# Page implementation
git add app/songs/page.tsx
git commit -m "feat(page): implement songs page with SSR

- Server Component data fetching
- Add search and filters
- Implement pagination"

# Dynamic routes
git add app/gallery/[id]/page.tsx
git commit -m "feat(page): add gallery detail page

- Dynamic route with params
- Image gallery with lightbox
- Add SEO metadata"
```

---

## Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Allowed Types

| Type | Use Case |
|------|----------|
| `init` | Project initialization |
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code refactoring |
| `config` | Configuration changes |
| `style` | Styling changes |
| `test` | Tests |
| `docs` | Documentation |

### Allowed Scopes

| Scope | Description |
|-------|-------------|
| `config` | Configuration files |
| `types` | Type definitions |
| `api` | API services |
| `hook` | Custom hooks |
| `component` | React components |
| `page` | Page components |
| `layout` | Layout components |
| `style` | Styling |
| `domain` | Domain layer |
| `infra` | Infrastructure layer |

### Subject Rules

- Use imperative mood ("add" not "added")
- Maximum 50 characters
- No period at the end
- Be specific and clear

---

## Special Workflows

### Tagging Milestones

Tag each phase completion:

```bash
# After Phase 1
git tag -a v0.1.0-init -m "Phase 1: Environment setup complete

- Next.js initialized
- TypeScript configured
- Tailwind setup"

# After Phase 2
git tag -a v0.2.0-foundation -m "Phase 2: Foundation complete

- DDD architecture migrated
- Types defined
- Layout created"

# After Phase 6 (before merge)
git tag -a v1.0.0-ready -m "Next.js migration ready for merge

- All pages migrated
- Tests passing
- Performance optimized"
```

### Preparing for Merge

Before merging into main repo:

```bash
# 1. Final commit
git add -A
git commit -m "chore: prepare for merge into main repo

- Final cleanup
- Update documentation
- Verify all tests pass"

# 2. Final tag
git tag -a v1.0.0-ready -m "Next.js migration complete"

# 3. Verify repository is clean
git status

# 4. Then follow merge workflow in Git workflow guide
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
# ... merge steps ...
```

---

## Verification Checklist

Before each commit:

- [ ] TypeScript compiles: `npx tsc --noEmit`
- [ ] No lint errors: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] Commit message follows format
- [ ] Related files staged together

Before tagging phase completion:

- [ ] All phase tasks complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Build successful
- [ ] No console errors

---

## Common Commands

```bash
# Development
cd repo/xxm_nextjs
npm run dev          # Start dev server

# Code quality
npx tsc --noEmit     # Type check
npm run lint         # Lint
npm run build        # Build

# Git
git status
git add -A
git commit -m "type(scope): description"
git tag -a v0.x.x -m "Phase x complete"

# View history
git log --oneline --graph
git log --oneline --all --graph  # Show tags
```

---

## Notes

- **No remote pushes**: This repo stays local until merged
- **Frequent commits**: Commit early and often during development
- **Clear messages**: Each commit should have a clear purpose
- **Phase tags**: Always tag phase completions for easy reference
- **Merge preparation**: Keep repo clean and ready for final merge
