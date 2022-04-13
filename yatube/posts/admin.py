"""Создание админской части сайта"""


from typing import Tuple
from django.contrib import admin

from posts.models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """Класс для админки постов"""
    list_display: Tuple[str, ...] = ('pk', 'text', 'pub_date',
                                     'author', 'group',)
    list_editable: Tuple[str, ...] = ('group',)
    search_fields: Tuple[str, ...] = ('text',)
    list_filter: Tuple[str, ...] = ('pub_date',)
    empty_value_display: str = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Класс для админки групп"""
    list_display: Tuple[str, ...] = ('title', 'description')
    list_editable: Tuple[str, ...] = ('description',)
    list_filter: Tuple[str, ...] = ('title',)
    empty_value_display: str = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
