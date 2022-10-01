from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    catname = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.catname}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=150)
    starting_bid = models.FloatField(max_length=64)
    is_active = models.BooleanField(default=True)
    image_url = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, related_name='listing_by_category')
    by = models.ForeignKey(User, on_delete=models.CASCADE,
                           related_name='my_listings')
    watchers = models.ManyToManyField(
        User, blank=True, related_name='my_watch_list')

    def __str__(self):
        return f"{self.title} - {self.starting_bid} ({self.by.username})"


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='bidders_list')
    by = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.FloatField()
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.listing.title} - {self.bid} (By : {self.by})"


class Comment(models.Model):
    comment = models.CharField(max_length=200)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name='comments_list')
    by = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.by.username}) commented on : {self.listing.title}"
