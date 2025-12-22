from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.urls import reverse

from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow

User = get_user_model()


def index(request):
    posts_all = Post.objects.all().order_by("-timestamp")
    paginator = Paginator(posts_all, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts
    })


def create_post(request):
    if request.method == "POST":
        content = request.POST["content"]
        image = request.FILES.get("image")
        user = request.user
        if content or image:
            post = Post(user=user, content=content, image=image)
            post.save()
        return HttpResponseRedirect(reverse("network:index"))


def profile(request, username):
    user_profile = User.objects.get(username=username)
    posts_all = user_profile.posts.all().order_by("-timestamp")
    paginator = Paginator(posts_all, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    followers = Follow.objects.filter(target=user_profile).count()
    following = Follow.objects.filter(user=user_profile).count()
    is_following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, target=user_profile).exists():
            is_following = True

    return render(request, "network/profile.html", {
        "user_profile": user_profile,
        "posts": posts,
        "followers": followers,
        "following": following,
        "is_following": is_following
    })


def follow(request, username):
    if request.method == "POST":
        user_to_follow = User.objects.get(username=username)
        if request.user == user_to_follow:
            return HttpResponseRedirect(reverse("network:profile", args=[username]))

        follow_obj = Follow.objects.filter(user=request.user, target=user_to_follow)
        if follow_obj.exists():
            follow_obj.delete()
        else:
            Follow.objects.create(user=request.user, target=user_to_follow)

        return HttpResponseRedirect(reverse("network:profile", args=[username]))


def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("network:login"))
    posts_all = Post.objects.filter(user__followers_relations__user=request.user).order_by("-timestamp")
    paginator = Paginator(posts_all, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
def edit(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        content = data.get("content")
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        if request.user != post.user:
            return JsonResponse({"error": "Permission denied"}, status=403)

        post.content = content
        post.save()
        return JsonResponse({"message": "Post updated successfully"}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)

    if request.method == "PUT":
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        return JsonResponse({"likes": post.likes.count(), "liked": liked}, status=200)
    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
@login_required
def edit_profile(request):
    if request.method == "POST":
        user = request.user

        # update text fields
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        if username:
            if User.objects.filter(username=username).exclude(pk=user.pk).exists():
                return JsonResponse({"error": "Username already taken."}, status=400)
            user.username = username

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        # update photo
        photo = request.FILES.get("profile_photo")
        if photo:
            user.profile_photo = photo

        user.save()
        return HttpResponseRedirect(reverse("network:profile", args=[user.username]))

    return HttpResponseRedirect(reverse("network:index"))


@csrf_exempt
@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")

        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        comment = Comment(user=request.user, post=post, content=content)
        comment.save()

        return JsonResponse({"message": "Comment added", "comment": comment.serialize()}, status=201)

    return JsonResponse({"error": "Invalid request method"}, status=400)
