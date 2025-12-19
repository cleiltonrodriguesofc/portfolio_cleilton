from django.conf import settings
from django.db import models
from django.utils import timezone




# create a model to leave comments
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    comment = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.comment}"

# create model to place bid
class Bid(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user} - {self.amount}"

# I renamed and modified the listing model to suit the project requirements, and be more descriptive
class Listing(models.Model):
    title = models.CharField(max_length=64)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True, max_length=500)
    description = models.TextField(default="No description", blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    # Listing categories
    CATEGORIES = [
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
        ('Home', 'Home'),
        ('Toys', 'Toys'),
        ('Other', 'Other'),
    ]
    category = models.CharField(max_length=64, choices=CATEGORIES, default='Other')
    # Listing owner
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    # Track if auction is open
    is_active = models.BooleanField(default=True)

    # get winner
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="won_auctions") 
    def get_biggest_bidder(self):
        biggest_bid = self.bid_set.order_by('-amount').first()
        return biggest_bid.user if biggest_bid else None 
    
    # Take listing to user's watchilist
    watchlist = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='watchlist')
    # get biggest bid to render in index
    def biggest_bid(self):
        return self.bid_set.order_by('-amount').first()

    
    
    
