from django.urls import path
from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:name>", views.entry, name="entry"),
    path("newpage/", views.newpage, name="newpage"),
    path("random/", views.randompage, name="random"),
    path("search/", views.search, name="search"),
    path("<str:name>/edit", views.edit_entry, name="edit"),
]