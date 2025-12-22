import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_cleilton.settings')
django.setup()

# Imports after setup to avoid AppRegistryNotReady
from commerce.models import Listing  # noqa: E402
from commerce.views import categories_bar  # noqa: E402

print("--- DEBUG INFO ---")
print(f"Categories Bar: {categories_bar}")
print("-" * 20)
print("Listings:")
for listing in Listing.objects.all():
    print(f"ID: {listing.id} | Title: '{listing.title}' | Category: '{listing.category}'")
print("-" * 20)
