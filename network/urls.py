
from django.urls import path

from . import views

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_comment/<int:post_id>", views.add_comment, name="add_comment"),
    path("create_post", views.create_post, name="create_post"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("follow/<str:username>", views.follow, name="follow"),
    path("following", views.following, name="following"),
    path("edit/<int:post_id>", views.edit, name="edit"),
    path("like/<int:post_id>", views.like_post, name="like_post")
]
