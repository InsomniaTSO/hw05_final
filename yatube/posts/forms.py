"""Создение форм"""
from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма создания и редактирования поста"""
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']


class CommentForm(forms.ModelForm):
    """Форма добавления комментария к посту"""
    class Meta:
        model = Comment
        fields = ['text']
