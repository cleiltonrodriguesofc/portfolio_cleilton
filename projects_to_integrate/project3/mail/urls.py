from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    # API Routes
    path("emails", views.compose, name="compose"),
    # path to access email content
    path("emails/<int:email_id>", views.email, name="email"),
    # path to load email box
    path("emails/<str:mailbox>", views.mailbox, name="mailbox"),
]
