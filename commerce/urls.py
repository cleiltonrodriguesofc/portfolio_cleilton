from django.urls import path

from . import views

app_name = "commerce"

urlpatterns = [
    path("", views.index, name="index"),
    path('<int:auction_id>', views.index, name='auction'),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("watchlist/toggle-watchlist/<int:listing_id>", views.toggle_watchlist, name="toggle_watchlist"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("category_listings/<str:category_name>", views.category_listings, name="category_listings"),
    path("listing/toggle-listing/<int:listing_id>", views.toggle_listing, name="toggle_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    
    
    path("login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
]
