from decimal import Decimal, ROUND_HALF_UP


class WeighingService:
    @staticmethod
    def calculate_net_weight(tara, loaded_weight):
        """
        Calculates net weight (Loaded - Tara).
        """
        return max(Decimal('0.0'), loaded_weight - tara)

    @staticmethod
    def calculate_sacks(net_weight, sack_weight_kg=60):
        """
        Calculates number of sacks from net weight.
        """
        if net_weight <= 0:
            return Decimal('0.00')

        sacks = net_weight / Decimal(str(sack_weight_kg))
        return sacks.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
