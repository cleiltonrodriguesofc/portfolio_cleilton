from django.db import models


class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('Ações', 'Ações'),
        ('FIIs', 'FIIs'),
        ('ETFs', 'ETFs'),
        ('Futuros', 'Futuros'),
        ('Outros', 'Outros'),
    ]

    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    asset_class = models.CharField(max_length=100)  # Full description e.g. PETR4 - C
    ticker = models.CharField(max_length=20)

    # Values
    liquid_value = models.DecimalField(max_digits=15, decimal_places=2)
    buy_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sell_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Metadata
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.ticker} ({self.liquid_value})"
