from decimal import Decimal


class FinanceService:
    @staticmethod
    def calculate_net_sale_per_sack(sale_price, freight_price):
        """
        Calculates net sale price per sack (Sale Price - Freight).
        """
        sale = sale_price or Decimal('0.0')
        freight = freight_price or Decimal('0.0')
        return sale - freight
