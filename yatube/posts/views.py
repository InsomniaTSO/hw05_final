"""Настройка views функций"""

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model

from django.conf import settings
from posts.models import Post, Group, Follow
from posts.forms import PostForm, CommentForm


User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    """Рендер главной страницы."""
    template = 'posts/index.html'
    text: str = 'Последние обновления на сайте.'
    post_list = Post.objects.select_related('group').all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'text': text,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_list(request: HttpRequest, slug: str) -> HttpResponse:
    """Рендер страницы сообщества."""
    template = 'posts/group_list.html'
    text: str = f'Записи сообщества: {slug}'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
        'text': text,
    }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """Рендер страницы пользователя."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    text: str = f'Профайл пользователя {author.get_full_name()}'
    quantity = post_list.count()
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_anonymous:
        following = False
    else:
        user = request.user
        following = Follow.objects.filter(user=user, author=author).exists()
    context = {
        'page_obj': page_obj,
        'text': text,
        'quantity': quantity,
        'author': author,
        'following': following
    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """Рендер страницы поста."""
    template = 'posts/post_detail.html'
    single_post = get_object_or_404(Post, id=post_id)
    text: str = f'{single_post.text}'[:30]
    single_post_author = single_post.author
    quantity = Post.objects.filter(author=single_post_author).count()
    form = CommentForm(request.POST or None)
    comments = single_post.comments.all()
    context = {
        'post': single_post,
        'text': text,
        'quantity': quantity,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    """Рендер страницы добавления поста."""
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if not form.is_valid():
        return render(request, template, {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('post:profile', username=request.user)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponse:
    """Рендер страницы редактирования поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('post:post_detail', post_id=post.id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    if not form.is_valid():
        return render(request, template, context)
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('post:post_detail', post_id=post.id)


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponse:
    """Рендер страницы добавления комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    '''Рендер страницы с постами отслеживаемых авторов.'''
    template = 'posts/follow.html'
    text: str = f'Подписки пользователя {request.user}'
    user = request.user
    post_list = Post.objects.filter(author__following__user=user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'text': text}
    return render(request, template, context)


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    '''Добавление подписки.'''
    user = request.user
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    '''Отмена подписки.'''
    user = request.user
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:follow_index')
