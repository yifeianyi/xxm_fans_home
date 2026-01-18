---
name: skill-create
description: Guide for creating new skills with proper structure, organization, and best practices
---

This skill provides comprehensive guidance for creating new skills in the iFlow framework.

## Skill Structure Overview

Each skill is a self-contained package with the following structure:

### Basic Structure (Simple Skills)

```
.iflow/skills/
└── skill-name/
    └── SKILL.md          # Main skill file (required)
```

### Modular Structure (Complex Skills)

```
.iflow/skills/
└── skill-name/
    ├── SKILL.md          # Main entry file (required)
    ├── module1.md        # Module-specific guide
    ├── module2.md        # Module-specific guide
    └── ...
```

## Creating a New Skill

### Step 1: Create Skill Directory

```bash
mkdir -p .iflow/skills/your-skill-name
```

### Step 2: Create Main SKILL.md File

The main file must include:

1. **YAML Frontmatter** (required)
2. **Skill Overview**
3. **Usage Instructions**
4. **Quick Reference** (if applicable)

### Step 3: Add Module Files (if needed)

For complex skills, create separate module files for detailed guidance.

## SKILL.md Template

```markdown
---
name: your-skill-name
description: Brief description of what this skill does
---

This skill provides [brief overview of skill purpose].

## Overview

[Provide a clear overview of what the skill does and when to use it]

## Usage

When to use this skill:
- Use case 1
- Use case 2
- Use case 3

## Quick Start

1. Step one
2. Step two
3. Step three

## Key Concepts

- Concept 1: [explanation]
- Concept 2: [explanation]
- Concept 3: [explanation]

## Examples

[Provide examples if applicable]

## Best Practices

- Best practice 1
- Best practice 2
- Best practice 3
```

## Modular Structure Template

For complex skills with multiple modules:

### Main SKILL.md

```markdown
---
name: your-skill-name
description: Brief description of what this skill does
---

This skill provides comprehensive guidance for [skill purpose].

## Overview

[High-level overview of the skill]

## Available Modules

1. **[Module 1](./module1.md)** - Module description
   - Purpose: What this module does
   - When to use: When you need to...

2. **[Module 2](./module2.md)** - Module description
   - Purpose: What this module does
   - When to use: When you need to...

## Usage

When asked to [skill action]:

1. **Identify the target module** - Determine which module you need
2. **Read the module-specific guide** - Access the corresponding .md file
3. **Apply module-specific standards** - Follow the patterns for that module

## Common Standards (All Modules)

[Standards that apply across all modules]

## Quick Reference

### When working with Module 1
→ Read [module1.md](./module1.md)

### When working with Module 2
→ Read [module2.md](./module2.md)

## Key Principles

- Principle 1
- Principle 2
- Principle 3
```

### Module File Template

```markdown
# Module Name Guide

## Module Overview

**Purpose**: [What this module does]

**Structure**: [File structure if applicable]

## Key Components

[Describe the main components of this module]

## Usage

[How to use this module]

## Standards

[Module-specific standards and conventions]

## Examples

[Examples specific to this module]

## Common Issues

[Common issues and solutions]

## Special Considerations

[Any special notes or considerations]
```

## Naming Conventions

### Skill Directory Name
- Use lowercase letters
- Use hyphens for multi-word names
- Examples: `django-model-formatter`, `frontend-design`, `api-integration`

### Skill Name (in frontmatter)
- Match directory name
- Use lowercase letters
- Use hyphens for multi-word names

### Description
- Keep it concise (1-2 sentences)
- Describe what the skill does
- Mention when to use it

## Best Practices

### 1. Keep It Focused
- Each skill should have a single, clear purpose
- Avoid making skills too broad or overlapping
- Split complex skills into modules if needed

### 2. Provide Clear Examples
- Include concrete examples
- Show both good and bad patterns
- Use real-world scenarios when possible

### 3. Use Modular Structure for Complex Skills
- If a skill has multiple distinct areas, use modules
- Main file should be an overview/navigation
- Module files contain detailed guidance
- Only read module files when needed

### 4. Include Quick Reference
- Provide a quick reference section
- Make it easy to find key information
- Use links to module files when applicable

### 5. Document Common Issues
- List common problems
- Provide solutions
- Include best practices to avoid issues

### 6. Use Consistent Formatting
- Use consistent heading levels
- Use code blocks for examples
- Use lists for multiple items
- Use bold for emphasis

## Examples of Existing Skills

### Simple Skill: frontend-design
```
.iflow/skills/frontend-design/
└── SKILL.md
```
- Single file with comprehensive guidance
- Focus on frontend design principles
- Includes design thinking and guidelines

### Modular Skill: django-model-formatter
```
.iflow/skills/module/
├── SKILL.md              # Main entry
├── song_management.md    # Module 1
├── fansdiy.md            # Module 2
├── site_settings.md      # Module 3
├── data_analytics.md     # Module 4
└── songlist.md           # Module 5
```
- Main file provides overview and navigation
- Module files contain detailed guidance for each app
- Each module is self-contained

## When to Use Modular Structure

Use modular structure when:

1. **Multiple Distinct Areas** - The skill covers multiple independent topics
2. **Large Content** - Single file would be too long (>200 lines)
3. **Independent Modules** - Users might only need specific modules
4. **Different Standards** - Different areas have different standards

Use single file structure when:

1. **Single Focus** - The skill covers one specific topic
2. **Moderate Content** - Content fits reasonably in one file (<200 lines)
3. **Unified Standards** - All content follows the same standards
4. **Simple Navigation** - No need for module-based navigation

## Skill Registration

Skills are automatically discovered by the iFlow framework. No registration needed.

To make a skill available:
1. Create the skill directory under `.iflow/skills/`
2. Create the `SKILL.md` file with proper frontmatter
3. The skill will be automatically available

## Testing Your Skill

After creating a skill:

1. **Verify Frontmatter** - Check YAML frontmatter is valid
2. **Test Links** - Ensure all internal links work
3. **Check Formatting** - Verify Markdown renders correctly
4. **Review Content** - Ensure content is clear and accurate
5. **Test Usage** - Try using the skill in practice

## Common Pitfalls

1. **Missing Frontmatter** - Always include YAML frontmatter
2. **Invalid YAML** - Ensure frontmatter is valid YAML
3. **Broken Links** - Check all internal links
4. **Poor Organization** - Structure content logically
5. **Missing Examples** - Include concrete examples
6. **Vague Description** - Make description clear and specific

## Skill Maintenance

Keep skills up-to-date by:

1. **Regular Review** - Review skills periodically
2. **Update Examples** - Keep examples current
3. **Add Best Practices** - Add new best practices as discovered
4. **Fix Issues** - Address reported issues
5. **Improve Clarity** - Enhance explanations based on usage

## Quick Checklist

Before considering a skill complete:

- [ ] Skill directory created
- [ ] SKILL.md file created with valid frontmatter
- [ ] Skill name matches directory name
- [ ] Description is clear and concise
- [ ] Overview provides context
- [ ] Usage instructions are clear
- [ ] Examples are included (if applicable)
- [ ] Common issues documented
- [ ] Best practices listed
- [ ] Links tested (if modular)
- [ ] Formatting consistent
- [ ] Content reviewed for accuracy

## Key Principles

- **Clarity** - Make instructions clear and easy to follow
- **Modularity** - Use modules for complex skills
- **Consistency** - Follow consistent patterns
- **Practicality** - Focus on practical guidance
- **Maintainability** - Keep skills up-to-date and relevant