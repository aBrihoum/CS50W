from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Bid, Comment


class Listing_form(forms.Form):
    title = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Title', 'class': 'form-control my-2', 'maxlength': '64'}))

    description = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Description', 'class': 'form-control my-2', 'maxlength': '300', 'rows': 5}))

    is_editing = forms.CharField(widget=forms.HiddenInput(), initial='False')

    listing_id = forms.CharField(widget=forms.HiddenInput(), initial='-1')

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        to_field_name='catname',
        required=False,
        empty_label="Select Category",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    starting_bid = forms.CharField(widget=forms.NumberInput(
        attrs={'placeholder': 'Starting bid (ex 150)', 'class': 'form-control my-2', 'maxlength': '64', 'step': '0.01'}))

    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(
        attrs={'class': 'form-check-input', 'id': 'switch'}))

    image_url = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'placeholder': 'https://example.com/image1.jpg', 'class': 'form-control my-2', 'maxlength': '300'}))


class Category_form(forms.Form):
    catname = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Category name', 'class': 'form-control my-2', 'maxlength': '64'}))


class Bid_form(forms.Form):
    bid = forms.CharField(widget=forms.NumberInput(
        attrs={'placeholder': 'Bid', 'class': 'form-control my-2', 'maxlength': '64', 'step': '0.01'}))


class Comment_form(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Add a comment', 'class': 'form-control my-2', 'maxlength': '200', 'rows': 3}))


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=True),
        "empty_message": 'There are no active listings !',
    })


def view_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    bids = Listing.objects.get(id=listing_id).bidders_list.all()
    comments = Listing.objects.get(id=listing_id).comments_list.all()
    latest_bid = float(listing.starting_bid)
    if (bids):
        latest_bid = float(bids.last().bid)
    context = {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "latest_bid": latest_bid,
        "comment_form": Comment_form(),
        "bid_form": Bid_form(),
    }
    if request.method == "POST":
        form = Bid_form(request.POST)
        if form.is_valid():
            bid = float(form.cleaned_data["bid"])
            context['error'] = False
            if (bid < latest_bid):
                context['error'] = 'Your bid must be at least as large as the current bid'
            elif (bid == latest_bid):
                if (bids):
                    if (bids.last().by == request.user):
                        context['error'] = 'You already have a bid with this value'
                    else:
                        context['error'] = 'Your bid must be higher than the current bid ($' + \
                            str(latest_bid)+')'
            if (context['error']):
                context['bid_form'] = form
                return render(request, "auctions/listing.html", context)
            else:
                Bid(listing=listing, by=request.user, bid=bid).save()
                return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
        else:
            context['error'] = form.errors
            return render(request, "auctions/listing.html", context)
    else:
        return render(request, "auctions/listing.html", context)


def closed_listings(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(is_active=False),
        "empty_message": 'There are no closed auctions !',
        "closed_listings": True
    })


@login_required(login_url='/login')
def watchlist(request):
    if request.method == "POST":
        listing = Listing.objects.get(id=request.POST['listing_id'])
        if request.user in listing.watchers.all():
            listing.watchers.remove(request.user)
        else:
            listing.watchers.add(request.user)
        return HttpResponseRedirect(reverse('view_listing', args=[request.POST['listing_id']]))
    else:
        return render(request, "auctions/index.html", {
            "listings": User.objects.get(id=request.user.id).my_watch_list.all(),
            "empty_message": 'Your watchlist is Empty !',
            "watchlist": True
        })


def category(request):
    if request.method == "POST":
        cat_id = request.POST['category_id']
        cat_name = Category.objects.get(id=cat_id).catname
        return render(request, "auctions/index.html", {
            "listings": Category.objects.get(id=cat_id).listing_by_category.filter(is_active=True),
            "empty_message": 'This category has no active listings !',
            "category_name": cat_name
        })
    else:
        return render(request, "auctions/categories.html", {
            "categories": Category.objects.all()
        })


@login_required(login_url='/login')
def my_listings(request):
    return render(request, "auctions/index.html", {
        "listings": User.objects.get(id=request.user.id).my_listings.all(),
        "my_listings": True,
        "empty_message": 'You have no active listings !',
    })


def listings_by(request, user):
    return render(request, "auctions/index.html", {
        "listings": User.objects.get(username=user).my_listings.all(),
        "my_listings": True,
        "empty_message": (f'({user}) have no active listings')
    })


@login_required(login_url='/login')
def new_listing(request):
    if request.method == "POST":
        form = Listing_form(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            is_active = form.cleaned_data["is_active"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            is_editing = form.cleaned_data["is_editing"]
            listing_id = int(form.cleaned_data["listing_id"])
            if (category):
                category = Category.objects.get(
                    catname=form.cleaned_data["category"])
            else:
                if (len(Category.objects.filter(catname='No category')) == 0):
                    Category(catname='No category').save()
                category = Category.objects.get(
                    catname='No category')
            if (image_url == ''):
                image_url = "/static/auctions/images/no-picture.png"
            if (is_editing == 'False'):
                Listing(title=title, description=description,
                        category=category, starting_bid=starting_bid, is_active=is_active, image_url=image_url, by=request.user).save()
            else:
                Listing.objects.filter(id=listing_id).update(title=title, description=description,
                                                             category=category, starting_bid=starting_bid, is_active=is_active, image_url=image_url)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new.html", {
                "form": form,
                "empty_input": form.errors
            })
    else:
        return render(request, "auctions/new.html", {
            "form": Listing_form(),
            "new_cat_form": Category_form(),
        })

# post


@login_required(login_url='/login')
def new_category(request):
    if request.method == "POST":
        form = Category_form(request.POST)
        if form.is_valid():
            catname = form.cleaned_data["catname"]
            try:
                Category(catname=catname).save()
            except IntegrityError:
                return render(request, "auctions/new.html", {
                    "form": Listing_form(),
                    "new_cat_form": Category_form(),
                    "cat_error": 'This category already exists'
                })
            return HttpResponseRedirect(reverse("new_listing"))
    else:
        return HttpResponseRedirect(reverse("new_listing"))


@login_required(login_url='/login')
def new_comment(request):
    if request.method == "POST":
        listing_id = request.POST['listing_id']
        listing = Listing.objects.get(id=listing_id)
        form = Comment_form(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["comment"]
            Comment(listing=listing, by=request.user, comment=comment).save()
            return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
        else:
            return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def delete_comment(request):
    if request.method == "POST":
        listing_id = request.POST['listing_id']
        comment_id = request.POST['comment_id']
        if (request.user != Comment.objects.get(id=comment_id).by):
            return HttpResponseRedirect(reverse("index"))
        Comment.objects.get(id=comment_id).delete()
        return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required(login_url='/login')
def listing_actions(request, action_type, listing_id):
    if (request.user != Listing.objects.get(id=listing_id).by):
        return HttpResponseRedirect(reverse("index"))
    if (action_type == 'delete'):
        Listing.objects.get(id=listing_id).delete()
        return HttpResponseRedirect(reverse("index"))
    elif (action_type == 'close'):
        Listing.objects.filter(id=listing_id).update(is_active=False)
        return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
    elif (action_type == 'open'):
        Listing.objects.filter(id=listing_id).update(is_active=True)
        return HttpResponseRedirect(reverse('view_listing', args=[listing_id]))
    elif (action_type == 'edit'):
        listing = Listing.objects.get(id=listing_id)
        form = Listing_form()
        form.fields['title'].initial = listing.title
        form.fields['description'].initial = listing.description
        form.fields['category'].initial = listing.category
        form.fields['starting_bid'].initial = listing.starting_bid
        form.fields['is_active'].initial = listing.is_active
        form.fields['image_url'].initial = listing.image_url
        form.fields['is_editing'].initial = "True"
        form.fields['listing_id'].initial = listing_id
        return render(request, "auctions/new.html", {
            "form": form,
            "new_cat_form": Category_form(),
        })


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next')
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
