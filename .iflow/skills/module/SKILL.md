---
name: django-model-formatter
description: Format Django database models with consistent structure, documentation, and best practices for the XXM Fans Home project
---

This skill provides comprehensive guidance for analyzing and formatting Django database models according to the XXM Fans Home project standards.

## Project Architecture Overview

The XXM Fans Home project uses a modular Django application structure with 5 core apps:

### Available Modules

1. **[song_management](./song_management.md)** - Core Music Management
   - Models: Song, SongRecord, Style, SongStyle, Tag, SongTag
   - Structure: Modular (models/ directory)
   - Purpose: Manage song information, performance records, styles, and tags

2. **[fansdiy](./fansdiy.md)** - Fan-created Content Management
   - Models: Collection, Work
   - Structure: Modular (models/ directory)
   - Purpose: Manage fan-created artwork collections and works

3. **[site_settings](./site_settings.md)** - Website Configuration
   - Models: SiteSettings, Recommendation
   - Structure: Modular (models/ directory)
   - Purpose: Manage global website settings and recommendations

4. **[data_analytics](./data_analytics.md)** - Data Analysis
   - Models: WorkStatic, WorkMetricsHour, CrawlSession
   - Structure: Single file (models.py)
   - Purpose: Track data analytics and crawling metrics

5. **[songlist](./songlist.md)** - Template-based Song Lists
   - Models: Dynamic models via ARTIST_CONFIG
   - Structure: Single file with dynamic model creation
   - Purpose: Lightweight, configurable song lists for different artists

## Usage

When asked to format or analyze Django models:

1. **Identify the target module** - Determine which app you're working with
2. **Read the module-specific guide** - Access the corresponding .md file for detailed instructions
3. **Apply module-specific standards** - Follow the patterns and conventions for that module
4. **Use common standards** - Refer to the formatting standards that apply across all modules

## Common Standards (All Modules)

### File Organization

**Modular Structure** (song_management, fansdiy, site_settings):
```
app_name/models/
├── __init__.py          # Export all models
├── model_name.py        # Model-specific files
└── signals.py           # Signal handlers (if needed)
```

**Single File** (data_analytics, songlist):
```
app_name/models.py       # All models in one file
```

### Basic Model Template

```python
"""Module description"""
from django.db import models


class ModelName(models.Model):
    """Brief model description"""

    field_name = models.CharField(
        max_length=200,
        verbose_name='Field Name',
        help_text='Field help text',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Model Name"
        verbose_name_plural = "Model Names"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['field_name']),
        ]

    def __str__(self):
        return f"{self.field_name}"
```

### Common Requirements

- **Language**: Use Chinese for `verbose_name` and docstrings
- **Documentation**: Add module and class docstrings
- **Indexes**: Add indexes on frequently queried fields
- **Timestamps**: Use `auto_now_add=True` and `auto_now=True`
- **Relationships**: Always use `related_name` for ForeignKey

## Quick Reference

### When working with song_management
→ Read [song_management.md](./song_management.md)

### When working with fansdiy
→ Read [fansdiy.md](./fansdiy.md)

### When working with site_settings
→ Read [site_settings.md](./site_settings.md)

### When working with data_analytics
→ Read [data_analytics.md](./data_analytics.md)

### When working with songlist
→ Read [songlist.md](./songlist.md)

## Key Principles

- **Consistency** - Follow uniform patterns within each module
- **Documentation** - Add comprehensive docstrings and verbose names
- **Performance** - Optimize with indexes and efficient queries
- **Maintainability** - Keep code clean and well-organized