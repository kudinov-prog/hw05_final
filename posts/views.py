from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, reverse
from django.shortcuts import get_object_or_404, get_list_or_404
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Comment, Follow


def page_not_found(request, exception):
    return render(
        request, 
        "misc/404.html", 
        {"path": request.path}, 
        status=404
    )


def server_error(request):
    return render(
        request,
        "misc/500.html",
        status=500
        )


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {"group": group, "page": page, "paginator": paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new.html', {'form': form})
    form = PostForm()
    return render(request, 'new.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    try:
        Follow.objects.get(author=author, user=request.user)
        following = True
    except:
        following = False
    return render(request, 'profile.html',
                  {'page': page, 'paginator': paginator,
                   'author': author, 'following': following})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(
        Post.objects.select_related('author'),
        id=post_id,
        author__username=username
    )
    form = CommentForm()
    comments = post.comments.all()
    return render(request, 'post.html', {'profile': user, 'post': post,
                                         'comments': comments, 'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post_url = reverse('post', args=(post.author, post_id))
    if post.author != request.user:
        return redirect(post_url)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect(post_url)
    return render(request, 'new.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.select_related('author').filter(
        author__following__user=request.user
        )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not request.user == author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)
