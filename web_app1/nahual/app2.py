from django import http
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_http_methods

from montgomery.forms import PostForm, CommentForm
from montgomery.models import Post
from montgomery.utils import get_model_for_date_and_slug


def show_post(request, year, month, day, slug):
    """Show information about a post."""
    post = get_model_for_date_and_slug(Post, year, month, day, slug)
    if not post.published and request.user.is_anonymous():
        return http.HttpResponseNotFound()
    form = CommentForm()
    form.fields["post"].initial = post.pk
    return render_to_response(
        "montgomery/show_post.html", {"post": post, "form": form}, context_instance=RequestContext(request)
    )


@login_required
def create_post(request):
    """Create new post."""
    form = PostForm()
    if request.method == "POST":
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # necessary to save tags
            return http.HttpResponseRedirect(post.get_absolute_url())
    return render_to_response("montgomery/create_post.html", {"form": form}, context_instance=RequestContext(request))


@login_required
def edit_post(request, year, month, day, slug):
    """Edit an existing blog post."""
    post = get_model_for_date_and_slug(Post, year, month, day, slug)
    form = PostForm(instance=post)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            if "continue_editing" in request.POST:
                return http.HttpResponseRedirect(post.get_edit_url())
            return http.HttpResponseRedirect(post.get_absolute_url())
    return render_to_response("montgomery/edit_post.html", {"form": form}, context_instance=RequestContext(request))


@login_required
@require_http_methods(["POST", "DELETE"])
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return http.HttpResponseForbidden()
    post.delete()
    if request.method == "DELETE":
        return http.HttpResponse(status=204)
    return http.HttpResponseRedirect("/")