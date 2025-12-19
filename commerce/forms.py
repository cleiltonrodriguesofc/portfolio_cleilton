from django import forms
from .models import Listing, Bid, Comment

# create a form to create a listing
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'starting_bid', 'image_url', 'description', 'category']
        widgets = {
            'description': forms.Textarea(),
        }

# craete a form to place a bid
class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

# create a form to comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']