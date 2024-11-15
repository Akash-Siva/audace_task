from django.db import models

# Create your models here.

class TokenData(models.Model):
    """
    Model to hold fetched data for commparison.
    """
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price_inr = models.DecimalField(max_digits=20, decimal_places=8)
    market_cap_inr = models.DecimalField(max_digits=20, decimal_places=2)
    volume_inr = models.DecimalField(max_digits=20, decimal_places=2)
    price_change_24h = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.symbol}) at {self.timestamp}"
