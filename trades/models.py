from decimal import Decimal
from django.conf import settings
from django.db import models

class Trades(models.Model):
    # ERD: Trades table (userID FK, side, ticker, shares, execPrice, execTimestamp)
    BUY, SELL = "BUY", "SELL"
    SIDE_CHOICES = [(BUY, "Buy"), (SELL, "Sell")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades")
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    ticker = models.CharField(max_length=12)  # e.g., "AAPL"
    shares = models.DecimalField(max_digits=18, decimal_places=6)      # positive
    exec_price = models.DecimalField(max_digits=18, decimal_places=6)  # positive
    exec_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "ticker", "exec_timestamp"]),
        ]
        constraints = [
            models.CheckConstraint(check=models.Q(shares__gt=0), name="trade_shares_positive"),
            models.CheckConstraint(check=models.Q(exec_price__gt=0), name="trade_price_positive"),
        ]

    def __str__(self):
        return f"{self.user.username} {self.side} {self.shares} {self.ticker} @ {self.exec_price}"


class Holdings(models.Model):
    # ERD: Holdings table (userID FK, ticker, quantity, avgCostBasis)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="holdings")
    ticker = models.CharField(max_length=12)
    quantity = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0"))       # ≥ 0
    avg_cost_basis = models.DecimalField(max_digits=18, decimal_places=6, default=Decimal("0")) # ≥ 0

    class Meta:
        unique_together = [("user", "ticker")]  # composite key from ERD
        indexes = [models.Index(fields=["user", "ticker"])]
        constraints = [
            models.CheckConstraint(check=models.Q(quantity__gte=0), name="holding_qty_nonneg"),
            models.CheckConstraint(check=models.Q(avg_cost_basis__gte=0), name="holding_acb_nonneg"),
        ]

    def __str__(self):
        return f"{self.user.username}:{self.ticker} {self.quantity} @ {self.avg_cost_basis}"
