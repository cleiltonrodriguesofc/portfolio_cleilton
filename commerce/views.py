from django.contrib.auth import authenticate, login, logout
# import decorator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
# import Forbiden to unauthorized request
from django.http import  HttpResponseRedirect #HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Listing, Bid, Comment
from .forms import BidForm, CommentForm
# import messages
from django.contrib import messages


# create a global variable to render categories in all pages
categories_bar = [category[0] for category in Listing.CATEGORIES]
def index(request):
    # render active listings
    active_listings = Listing.objects.filter(is_active=True)
    # listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": active_listings, 
        "categories": categories_bar,
    })

# toggle listing 
@login_required
def toggle_listing(request, listing_id):
    if request.method == 'POST':
        # get listing
        listing = get_object_or_404(Listing, pk=listing_id)
        # verify if listing is active
        if request.user == listing.user:
            biggest_bidder = listing.get_biggest_bidder()
            listing.winner = biggest_bidder
            listing.is_active = not listing.is_active
            # listing.closed_auction = not listing.closed_auction
            listing.save()
    return HttpResponseRedirect(reverse("commerce:index"))


# ensure user is authenticated
# create a function to render watchlist
@login_required(login_url='commerce:login')
def watchlist(request): 
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "categories": categories_bar
    })

# create a function to toggle listing
@login_required(login_url='commerce:login')
def toggle_watchlist(request, listing_id):
    if request.method == 'POST':
        # get listing
        listing = Listing.objects.get(pk=listing_id)
        # get logged in user
        user = request.user
        # verify if listing is not in user's watchlist, and put them
        if listing not in user.watchlist.all():
            user.watchlist.add(listing)
        # else, remove it
        else:
            user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse("commerce:listing", args=(listing_id,)))



# show listings in category
def category_listings(request, category_name):
    listings = Listing.objects.filter(category=category_name).all()
    return render(request, "auctions/category_listings.html", {
        "listings": listings,
        "category_name": category_name, 
        "categories": categories_bar
    })

@login_required(login_url='commerce:login')
def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    # render comments
    comments = Comment.objects.filter(listing=listing).order_by('-created_date').all() 
    # get a listing
    listing = Listing.objects.get(id=listing_id)
    # list bids
    bids = Bid.objects.filter(listing=listing).order_by('-amount').all()
    # get the biggest bid
    biggest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()
    # toggle auction, handling the toggle functionality
    if request.method == 'POST':
        # render bid form and biggest bid
        form_bid = BidForm(request.POST)
        if form_bid.is_valid():
             # Create bid but don't save yet
            bid = form_bid.save(commit=False) 
            # Get current highest bid
            biggest_bid = listing.biggest_bid() 
            if biggest_bid is None or bid.amount > biggest_bid.amount:  
                bid.user = request.user
                bid.listing = listing
                if listing not in request.user.watchlist.all():
                    request.user.watchlist.add(listing)
                bid.save()
            else:
                # render entiry page
                form_bid = BidForm()
                comment_form = CommentForm()
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "form_bid": form_bid,
                    # render an error message
                    "message": "Your bid must be bigger.",
                    "bids": bids,
                    "biggest_bid": biggest_bid,
                    "comments": comments,
                    "category_listings": category_listings,
                    "categories": categories_bar,
                    'comment_form': comment_form
                 })

            return HttpResponseRedirect(reverse("commerce:listing", args=(listing_id,)))   

        # render comment form and comments
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.listing =  listing
            comment.save()
            return HttpResponseRedirect(reverse("commerce:listing", args=(listing_id,)))
    
    else:
        form_bid = BidForm()
        comment_form = CommentForm()

        return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "biggest_bid": biggest_bid,
        "form_bid": form_bid,
        "comments": comments,
        "category_listings": category_listings,
        "categories": categories_bar,
        'comment_form': comment_form,
        })


# ensure user is authenticated
@login_required(login_url='commerce:login')
# def create_listing
def create_listing(request):
    if request.method == "POST":
        # get form
        title = request.POST['title']
        starting_bid = request.POST['starting_bid']
        image_url = request.POST['image_url']
        description = request.POST['description']
        category = request.POST['category']

        listing = Listing.objects.create(
            user=request.user,
            title=title,
            starting_bid=starting_bid, 
            image_url=image_url, 
            description=description, 
            category=category
            )
        listing.user = request.user
        listing.save()
        return HttpResponseRedirect(reverse("commerce:index"))
   
    return render(request, "auctions/create_listing.html", {
        # "form": form,
        "categories": categories_bar
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
            return HttpResponseRedirect(reverse("commerce:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password.",
                "categories": categories_bar
            })
    else:
        return render(request, "auctions/login.html", {
            "categories": categories_bar
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("commerce:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        # add first and last name
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # ensure all fields are filled
        if not username and not password and not email:
            return render(request, "auctions/register.html", {
                "message": "All fields are required.",
                "categories": categories_bar
            })


        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match.",
                "categories": categories_bar
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            # add first and last name
            user.first_name = first_name
            user.last_name = last_name
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken.",
                "categories": categories_bar
            })
        
        login(request, user)
        return HttpResponseRedirect(reverse("commerce:index"))
    else:
        return render(request, "auctions/register.html", {
            "categories": categories_bar
        })
