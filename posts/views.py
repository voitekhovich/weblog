from django.conf import settings as set
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

User = get_user_model()


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, set.PAGE_ITEMS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, set.PAGE_ITEMS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html',
        {'group': group, 'page': page})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')

    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    following = None
    if user.is_active:
        following = Follow.objects.filter(user=user, author=author)
    # posts = Post.objects.filter(author=author)
    posts = author.posts.all()
    posts_count = posts.count()
    paginator = Paginator(posts, set.PAGE_ITEMS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {
        'author': author,
        'page': page,
        # 'posts_count': posts_count,
        'following': following, })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    posts_count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm()
    return render(request, 'post.html', {
        'form': form,
        'post': post,
        'posts_count': posts_count,
        'author': post.author,
        'comments': comments,
    })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)

    form = PostForm(instance=post)
    return render(request, 'new.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)

    return render(request, 'post.html', {'form': form})


@login_required
def follow_index(request):
    user = request.user
    posts = Post.objects.filter(author__following__user=user)
    paginator = Paginator(posts, set.PAGE_ITEMS)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user

    follow = Follow.objects.filter(user=user, author=author).exists()

    if author == user or follow:
        return redirect('profile', username=username)

    Follow.objects.create(
        user=user,
        author=author,
    )
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    object = Follow.objects.filter(user=user, author__username=username)
    if object.exists():
        object.delete()
    return redirect('profile', username=username)
