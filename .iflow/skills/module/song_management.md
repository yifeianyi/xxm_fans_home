# song_management Module Guide

## Module Overview

**Purpose**: Manage song information, performance records, styles, and tags

**Structure**: Modular (models/ directory with separate files)

## Models

### 1. Song
**File**: `models/song.py`

**Purpose**: Core song model storing basic song information

**Key Fields**:
- `song_name` - Song name (required)
- `singer` - Original singer (optional)
- `first_perform` - First performance date (optional)
- `last_performed` - Last performance date (optional)
- `perform_count` - Number of performances (default: 0)
- `language` - Song language (optional)

**Properties**:
- `styles` - Get list of style names
- `tags` - Get list of tag names

**Indexes**: song_name, singer, language

### 2. SongRecord
**File**: `models/song.py`

**Purpose**: Track individual performance records

**Key Fields**:
- `song` - ForeignKey to Song (required)
- `performed_at` - Performance date (required)
- `url` - Video link (optional)
- `notes` - Performance notes (optional)
- `cover_url` - Cover image URL (optional)

**Relationship**: One Song has many SongRecords

**Ordering**: -performed_at (most recent first)

### 3. Style
**File**: `models/style.py`

**Purpose**: Define music styles/genres

**Key Fields**:
- `name` - Style name (unique, required)
- `description` - Style description (optional)

**Ordering**: name (alphabetical)

### 4. SongStyle
**File**: `models/style.py`

**Purpose**: Many-to-many relationship between Song and Style

**Key Fields**:
- `song` - ForeignKey to Song
- `style` - ForeignKey to Style

**Constraint**: unique_together (song, style)

### 5. Tag
**File**: `models/tag.py`

**Purpose**: Define tags for categorization

**Key Fields**:
- `name` - Tag name (unique, required)
- `description` - Tag description (optional)

**Ordering**: name (alphabetical)

### 6. SongTag
**File**: `models/tag.py`

**Purpose**: Many-to-many relationship between Song and Tag

**Key Fields**:
- `song` - ForeignKey to Song
- `tag` - ForeignKey to Tag

**Constraint**: unique_together (song, tag)

## File Structure

```
song_management/models/
├── __init__.py          # Exports: Song, SongRecord, Style, SongStyle, Tag, SongTag
├── song.py              # Song, SongRecord models
├── style.py             # Style, SongStyle models
├── tag.py               # Tag, SongTag models
└── signals.py           # Signal handlers
```

## __init__.py Template

```python
"""Song Management 模型"""
from .song import Song, SongRecord
from .style import Style, SongStyle
from .tag import Tag, SongTag

# Import signal handlers
from . import signals

__all__ = [
    'Song',
    'SongRecord',
    'Style',
    'SongStyle',
    'Tag',
    'SongTag',
]
```

## Formatting Standards

### Song Model Template

```python
"""歌曲相关模型"""
from django.db import models


class Song(models.Model):
    """歌曲模型"""
    song_name = models.CharField(
        max_length=200,
        verbose_name='歌曲名称'
    )
    singer = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='歌手'
    )
    first_perform = models.DateField(
        blank=True,
        null=True,
        verbose_name='首次演唱时间'
    )
    last_performed = models.DateField(
        blank=True,
        null=True,
        verbose_name='最近演唱时间'
    )
    perform_count = models.IntegerField(
        default=0,
        verbose_name='演唱次数'
    )
    language = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='语言'
    )

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"
        ordering = ['song_name']
        indexes = [
            models.Index(fields=['song_name']),
            models.Index(fields=['singer']),
            models.Index(fields=['language']),
        ]

    def __str__(self):
        return self.song_name

    @property
    def styles(self):
        """获取歌曲的曲风列表"""
        return [song_style.style.name for song_style in self.song_styles.all()]

    @property
    def tags(self):
        """获取歌曲的标签列表"""
        return [song_tag.tag.name for song_tag in self.song_tags.all()]
```

### SongRecord Model Template

```python
class SongRecord(models.Model):
    """演唱记录模型"""
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='歌曲'
    )
    performed_at = models.DateField(verbose_name='演唱时间')
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name='视频链接'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    cover_url = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='封面URL'
    )

    class Meta:
        verbose_name = "演唱记录"
        verbose_name_plural = "演唱记录"
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.song.song_name} @ {self.performed_at}"
```

## Common Issues

1. **Missing indexes on Song** - Ensure indexes on song_name, singer, language
2. **No related_name on SongRecord** - Should use related_name='records'
3. **Missing verbose_name** - All fields need Chinese verbose_name
4. **No docstrings** - Add module and class docstrings
5. **Poor ordering** - Song should order by song_name, SongRecord by -performed_at

## Special Considerations

- Song is the core model, all other models relate to it
- Use properties (styles, tags) for computed fields
- SongRecord should cascade delete when Song is deleted
- Style and Tag are reusable across multiple songs