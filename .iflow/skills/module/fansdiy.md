# fansDIY Module Guide

## Module Overview

**Purpose**: Manage fan-created artwork collections and individual works

**Structure**: Modular (models/ directory with separate files)

## Models

### 1. Collection
**File**: `models/collection.py`

**Purpose**: Group related fan-created works into collections

**Key Fields**:
- `name` - Collection name (required)
- `works_count` - Number of works in collection (default: 0)
- `display_order` - Display order (default: 0)
- `position` - Position (default: 0)
- `created_at` - Creation timestamp (auto)
- `updated_at` - Update timestamp (auto)

**Methods**:
- `update_works_count()` - Update the count of related works

**Relationship**: One Collection has many Works

**Ordering**: position, display_order, -created_at

### 2. Work
**File**: `models/work.py`

**Purpose**: Individual fan-created artwork

**Key Fields**:
- `collection` - ForeignKey to Collection (required)
- `title` - Work title (required)
- `cover_url` - Cover image URL (optional)
- `view_url` - View link (optional)
- `author` - Author name (required)
- `notes` - Notes (optional)
- `display_order` - Display order (default: 0)
- `position` - Position (default: 0)

**Methods**:
- `save()` - Auto-updates collection's works_count
- `delete()` - Auto-updates collection's works_count

**Relationship**: Many Works belong to one Collection

**Ordering**: position, display_order, -id

## File Structure

```
fansDIY/models/
├── __init__.py          # Exports: Collection, Work
├── collection.py        # Collection model
├── work.py              # Work model
└── signals.py           # Signal handlers (if needed)
```

## __init__.py Template

```python
from .collection import Collection
from .work import Work

__all__ = ['Collection', 'Work']
```

## Formatting Standards

### Collection Model Template

```python
from django.db import models


class Collection(models.Model):
    """粉丝二创合集"""
    name = models.CharField(
        max_length=200,
        verbose_name="合集名称"
    )
    works_count = models.IntegerField(
        default=0,
        verbose_name="作品数量"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="显示顺序"
    )
    position = models.IntegerField(
        default=0,
        verbose_name="位置"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )

    class Meta:
        verbose_name = "二创合集"
        verbose_name_plural = "二创合集"
        ordering = ['position', 'display_order', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.works_count}个作品)"

    def update_works_count(self):
        """更新作品数量"""
        self.works_count = self.works.count()
        self.save(update_fields=['works_count'])
```

### Work Model Template

```python
from django.db import models


class Work(models.Model):
    """作品记录"""
    collection = models.ForeignKey(
        'Collection',
        on_delete=models.CASCADE,
        related_name='works',
        verbose_name="所属合集"
    )
    title = models.CharField(
        max_length=300,
        verbose_name="作品标题"
    )
    cover_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="封面图片地址"
    )
    view_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="观看链接"
    )
    author = models.CharField(
        max_length=100,
        verbose_name="作者"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="备注"
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name="显示顺序"
    )
    position = models.IntegerField(
        default=0,
        verbose_name="位置"
    )

    class Meta:
        verbose_name = "作品记录"
        verbose_name_plural = "作品记录"
        ordering = ['position', 'display_order', '-id']

    def __str__(self):
        return f"{self.title} - {self.author}"

    def save(self, *args, **kwargs):
        """保存时自动更新合集的作品数量"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.collection.update_works_count()

    def delete(self, *args, **kwargs):
        """删除时自动更新合集的作品数量"""
        collection = self.collection
        super().delete(*args, **kwargs)
        collection.update_works_count()
```

## Special Pattern: Self-updating Counts

This module demonstrates the self-updating count pattern:

```python
class Collection(models.Model):
    works_count = models.IntegerField(default=0, verbose_name="作品数量")

    def update_works_count(self):
        """Update the count of related works"""
        self.works_count = self.works.count()
        self.save(update_fields=['works_count'])

class Work(models.Model):
    collection = models.ForeignKey('Collection', ...)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.collection.update_works_count()

    def delete(self, *args, **kwargs):
        collection = self.collection
        super().delete(*args, **kwargs)
        collection.update_works_count()
```

**Key Points**:
- Use `update_fields` to avoid unnecessary updates
- Check `self.pk is None` to detect new objects
- Cache the related object before deletion

## Common Issues

1. **Missing related_name** - Work must use related_name='works'
2. **No auto-update on save/delete** - Works should update collection's works_count
3. **Missing verbose_name** - All fields need Chinese verbose_name
4. **No docstrings** - Add module and class docstrings
5. **Poor ordering** - Collections should order by position, display_order, -created_at

## Special Considerations

- Works must cascade delete when Collection is deleted
- works_count should always be accurate
- Use position and display_order for custom sorting
- Collection __str__ should include works_count