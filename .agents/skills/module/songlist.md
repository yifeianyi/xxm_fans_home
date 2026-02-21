# songlist Module Guide

## Module Overview

**Purpose**: Provide lightweight, configurable song lists for different artists

**Structure**: Single file with dynamic model creation

## Dynamic Models

### Configuration

```python
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
}
```

### Generated Models

For each artist in ARTIST_CONFIG, two models are created:

1. **{Artist}Song** - Song model for specific artist
2. **{Artist}SiteSetting** - Site setting model for specific artist

### Example Models

- YouyouSong, YouyouSiteSetting
- BingjieSong, BingjieSiteSetting

## File Structure

```
songlist/
└── models.py            # Dynamic model creation
```

## Formatting Standards

### Dynamic Model Creation Template

```python
from django.db import models


# 歌手配置字典（一句话配置一个歌手）
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
}


def create_artist_models(artist_key, artist_name):
    """同时创建歌手的Song和SiteSetting模型"""
    class_name = artist_key.capitalize()  # youyou -> Youyou, bingjie -> Bingjie

    # 创建Song模型
    class SongMeta:
        verbose_name = f'{artist_name}歌曲'
        verbose_name_plural = f'{artist_name}歌曲'
        app_label = 'songlist'
        ordering = ['song_name']

    song_attrs = {
        '__module__': 'songlist.models',
        'song_name': models.CharField(max_length=200, verbose_name='歌曲名称'),
        'singer': models.CharField(max_length=100, verbose_name='原唱歌手'),
        'language': models.CharField(max_length=50, verbose_name='语言'),
        'style': models.CharField(max_length=50, verbose_name='曲风'),
        'note': models.TextField(blank=True, verbose_name='备注'),
        'Meta': SongMeta,
        '__str__': lambda self: self.song_name,
    }

    song_model = type(f'{class_name}Song', (models.Model,), song_attrs)

    # 创建SiteSetting模型
    class SettingMeta:
        verbose_name = f'{artist_name}网站设置'
        verbose_name_plural = f'{artist_name}网站设置'
        app_label = 'songlist'

    setting_attrs = {
        '__module__': 'songlist.models',
        'photo_url': models.CharField(max_length=500, verbose_name='图片URL'),
        'position': models.IntegerField(
            verbose_name='位置',
            choices=[
                (1, '头像图标'),
                (2, '背景图片'),
            ]
        ),
        'Meta': SettingMeta,
        '__str__': lambda self: f"设置 - 位置: {self.get_position_display()}",
    }

    setting_model = type(f'{class_name}SiteSetting', (models.Model,), setting_attrs)

    return song_model, setting_model


# 动态创建所有歌手的模型
for artist_key, artist_name in ARTIST_CONFIG.items():
    song_model, setting_model = create_artist_models(artist_key, artist_name)
    class_name = artist_key.capitalize()
    globals()[f'{class_name}Song'] = song_model
    globals()[f'{class_name}SiteSetting'] = setting_model


# 导出模型供其他模块使用
YouyouSong = globals()['YouyouSong']
BingjieSong = globals()['BingjieSong']
YouyouSiteSetting = globals()['YouyouSiteSetting']
BingjieSiteSetting = globals()['BingjieSiteSetting']


# 将模型添加到模块的 __all__ 中，确保Django能正确识别
__all__ = ['YouyouSong', 'BingjieSong', 'YouyouSiteSetting', 'BingjieSiteSetting']
```

## Special Pattern: Dynamic Model Creation

This module demonstrates dynamic model creation:

```python
def create_artist_models(artist_key, artist_name):
    """Create dynamic models for an artist"""
    class_name = artist_key.capitalize()

    # Create Song model
    song_attrs = {
        '__module__': 'songlist.models',
        'song_name': models.CharField(max_length=200, verbose_name='歌曲名称'),
        'Meta': type('Meta', (), {
            'verbose_name': f'{artist_name}歌曲',
            'verbose_name_plural': f'{artist_name}歌曲',
            'app_label': 'songlist',
            'ordering': ['song_name']
        }),
        '__str__': lambda self: self.song_name,
    }

    return type(f'{class_name}Song', (models.Model,), song_attrs)
```

**Key Points**:
- Use `type()` to dynamically create model classes
- Set `__module__` to ensure proper Django registration
- Use `globals()` to make models accessible
- Export models in `__all__` for Django's model discovery

## Common Issues

1. **Missing __module__** - Dynamic models need __module__ set to 'songlist.models'
2. **Missing app_label** - Meta class must include app_label='songlist'
3. **No __all__ export** - Models must be in __all__ for Django discovery
4. **Incorrect class naming** - Use capitalize() for consistent naming
5. **Missing verbose_name** - All fields need Chinese verbose_name

## Special Considerations

- Models are created dynamically from ARTIST_CONFIG
- Each artist gets independent models (no cross-artist relationships)
- Adding a new artist is as simple as adding to ARTIST_CONFIG
- Requires migrations for each new artist added
- Models are lightweight and independent of other apps

## Adding a New Artist

To add a new artist:

1. Add to ARTIST_CONFIG:
```python
ARTIST_CONFIG = {
    'youyou': '乐游',
    'bingjie': '冰洁',
    'newartist': '新歌手',  # Add this
}
```

2. Run migrations:
```bash
python manage.py makemigrations songlist
python manage.py migrate songlist --database=songlist_db
```

3. Update __all__ to include new models (or make it dynamic)