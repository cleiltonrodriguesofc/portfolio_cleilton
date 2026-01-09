from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'ticker', 'category', 'liquid_value')
    list_filter = ('category', 'date')
    search_fields = ('ticker', 'asset_class')
