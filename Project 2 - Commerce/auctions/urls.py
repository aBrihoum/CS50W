from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:listing_id>", views.view_listing, name="view_listing"),
    path("closed_listings", views.closed_listings, name="closed_listings"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("user/<str:user>", views.listings_by, name="listings_by"),
    # post
    path("new_category", views.new_category, name="new_category"),
    path("new_comment", views.new_comment, name="new_comment"),
    path("delete_comment", views.delete_comment, name="delete_comment"),
    path("listing_actions/<str:action_type>/<int:listing_id>",
         views.listing_actions, name="listing_actions"),
    #
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
