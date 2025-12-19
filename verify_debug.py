import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_cleilton.settings')
django.setup()

from commerce.models import Listing
from commerce.views import categories_bar

print("--- DEBUG INFO ---")
print(f"Categories Bar: {categories_bar}")
print("-" * 20)
print("Listings:")
for l in Listing.objects.all():
    print(f"ID: {l.id} | Title: '{l.title}' | Category: '{l.category}'")
print("-" * 20)
