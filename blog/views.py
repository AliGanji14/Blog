from django.views.decorators.http import require_POST
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.mail import send_mail

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, id):
    post = get_object_or_404(Post, pk=id, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    return render(request, 'blog/post_detail.html', {'post': post, 'comments': comments, 'form': form})


def post_share(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, settings.EMAIL_HOST_USER,
                      [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post_share.html', {'form': form, 'post': post, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/comment.html', {'post': post, 'form': form, 'comment': comment})
