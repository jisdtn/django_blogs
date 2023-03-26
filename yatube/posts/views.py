from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import AMOUNT_POSTS_NUMBER

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    title = "Последние обновления на сайте"
    posts = Post.objects.order_by("-pub_date")
    paginator = Paginator(posts, AMOUNT_POSTS_NUMBER)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "title": title,
        "page_obj": page_obj,
        "posts": posts,
    }
    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    title = 'Записи сообщества'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.order_by("-pub_date")
    paginator = Paginator(posts, AMOUNT_POSTS_NUMBER)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "title": title,
        "page_obj": page_obj,
        "group": group,
        "posts": posts,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if request.user.is_authenticated and request.user != author:
        following = Follow.objects.filter(
            'user',
            'author'
        ).exists()
    else:
        following = False

    post_list = author.posts.order_by("-pub_date")

    paginator = Paginator(post_list, AMOUNT_POSTS_NUMBER)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    post_count = post_list.count()

    context = {
        "author": author,
        "page_obj": page_obj,
        "post_count": post_count,
        "username": username,
        'following': following,
    }
    return render(request, "posts/profile.html", context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    comments = post.comments.all()

    form = CommentForm(request.POST or None)
    context = {
        "post": post,
        "post_count": post_count,
        'form': form,
        'comments': comments,
    }
    return render(request, "posts/post_detail.html", context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect("posts:profile", username=post.author.username)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)

    return render(request, "posts/create_post.html", {
        "form": form, "is_edit": is_edit
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    title = 'Подписки'
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, AMOUNT_POSTS_NUMBER)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and Follow.objects.filter(
        user=request.user,
        author=author
    ).exists() == False:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username)
