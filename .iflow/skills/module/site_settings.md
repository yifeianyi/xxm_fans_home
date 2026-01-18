# site_settings Module Guide

## Module Overview

**Purpose**: Manage global website settings and recommendations

**Structure**: Modular (models/ directory with separate files)

## Models

### 1. SiteSettings
**File**: `models/settings.py`

**Purpose**: Store global website configuration

**Key Fields**:
- `favicon` - Website icon image (optional)
- `created_at` - Creation timestamp (auto)
- `updated_at` - Update timestamp (auto)

**Methods**:
- `favicon_url()` - Return favicon URL path

**Note**: Singleton pattern - typically only one record

### 2. Recommendation
**File**: `models/settings.py`

**Purpose**: Store recommendation content and related songs

**Key Fields**:
- `content` - Recommendation text (required)
- `recommended_songs` - ManyToMany to Song (optional)
- `is_active` - Whether to display (default: True)
- `created_at` - Creation timestamp (auto)
- `updated_at` - Update timestamp (auto)

**Relationship**: Many-to-many with Song (song_management.Song)

**Ordering**: -created_at (most recent first)

## File Structure

```
site_settings/models/
├── __init__.py          # Exports: SiteSettings, Recommendation
└── settings.py          # SiteSettings, Recommendation models
```

## __init__.py Template

```python
from .settings import SiteSettings, Recommendation

__all__ = ['SiteSettings', 'Recommendation']
```

## Formatting Standards

### SiteSettings Model Template

```python
from django.db import models


class SiteSettings(models.Model):
    """网站设置模型"""
    favicon = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name="网站图标"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def __str__(self):
        return "网站设置"

    def favicon_url(self):
        """返回favicon的URL路径"""
        if self.favicon:
            return self.favicon.url
        return None
```

### Recommendation Model Template

```python
from django.db import models


class Recommendation(models.Model):
    """推荐语模型"""
    content = models.TextField(
        help_text="推荐语内容"
    )
    recommended_songs = models.ManyToManyField(
        'song_management.Song',
        blank=True,
        help_text="推荐的歌曲",
        related_name='recommendations'
    )
    is_active = models.BooleanField(
        default=True,
        help_text="是否激活显示"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = "推荐语"
        verbose_name_plural = "推荐语"
        ordering = ['-created_at']

    def __str__(self):
        if len(self.content) > 50:
            return f"推荐语: {self.content[:50]}..."
        return f"推荐语: {self.content}"
```

## Common Issues

1. **Missing related_name** - Recommendation must use related_name='recommendations'
2. **No help_text** - Recommendation fields need helpful descriptions
3. **Missing verbose_name** - All fields need Chinese verbose_name
4. **No docstrings** - Add module and class docstrings
5. **Poor __str__ method** - Should truncate long content

## Special Considerations

- SiteSettings is typically a singleton (only one record)
- Recommendation can have multiple active records
- ImageField requires proper MEDIA_ROOT/MEDIA_URL configuration
- ManyToMany relationship with Song requires proper app label ('song_management.Song')
- Use help_text for user-facing fields in admin interface