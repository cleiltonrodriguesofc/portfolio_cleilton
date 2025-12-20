from django.urls import path
from . import views

app_name = "search"

urlpatterns = [
    path("", views.index, name="index"),
    path("image/", views.image, name="image"),
    path("advanced/", views.advanced, name="advanced"),
]
