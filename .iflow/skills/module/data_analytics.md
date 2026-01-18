# data_analytics Module Guide

## Module Overview

**Purpose**: Track data analytics and crawling metrics

**Structure**: Single file (models.py)

## Models

### 1. WorkStatic
**Purpose**: Store static information about works

**Key Fields**:
- `related_song` - ForeignKey to Song (optional)
- Other analytics fields (to be defined)

**Relationship**: Optional relationship with Song (song_management.Song)

### 2. WorkMetricsHour
**Purpose**: Track hourly metrics for works

**Key Fields**:
- `work_static` - ForeignKey to WorkStatic
- Hourly metrics fields (to be defined)

**Relationship**: One WorkStatic has many WorkMetricsHour

### 3. CrawlSession
**Purpose**: Track crawling sessions

**Key Fields**:
- Session tracking fields (to be defined)

**Relationship**: Related to WorkStatic

## File Structure

```
data_analytics/
└── models.py            # All models in one file
```

## Formatting Standards

### Single File Template

```python
from django.db import models


class WorkStatic(models.Model):
    """作品静态信息"""
    related_song = models.ForeignKey(
        'song_management.Song',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_static',
        verbose_name='关联歌曲'
    )

    class Meta:
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"

    def __str__(self):
        return f"WorkStatic {self.id}"


class WorkMetricsHour(models.Model):
    """小时级指标追踪"""
    work_static = models.ForeignKey(
        WorkStatic,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name='作品静态信息'
    )

    class Meta:
        verbose_name = "小时级指标"
        verbose_name_plural = "小时级指标"

    def __str__(self):
        return f"Metrics for {self.work_static}"


class CrawlSession(models.Model):
    """爬取任务管理"""
    # Add fields as needed

    class Meta:
        verbose_name = "爬取任务"
        verbose_name_plural = "爬取任务"

    def __str__(self):
        return f"CrawlSession {self.id}"
```

## Common Issues

1. **Missing related_name** - ForeignKeys need related_name
2. **No on_delete specified** - Always specify on_delete behavior
3. **Missing verbose_name** - All fields need Chinese verbose_name
4. **No docstrings** - Add module and class docstrings
5. **Poor ordering** - Set appropriate default ordering in Meta class

## Special Considerations

- This module uses single file structure (not modular)
- related_song is optional (SET_NULL for soft deletion)
- WorkMetricsHour tracks time-series data
- CrawlSession manages data collection tasks
- All models in one file for simplicity

## Data Relationships

- WorkStatic → Song (optional, via related_song)
- WorkStatic → WorkMetricsHour (one-to-many)
- WorkStatic → CrawlSession (relationship to be defined based on needs)