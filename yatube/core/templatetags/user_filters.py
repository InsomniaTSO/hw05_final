from django.forms import BoundField

from django import template

register = template.Library()


@register.filter
def addclass(field: BoundField, css: str) -> str:
    """Фильтр для добавления CSS-классов в теги"""
    return field.as_widget(attrs={'class': css})
