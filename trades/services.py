from .models import Trades, Holdings
from tradeGround.alpaca_request import fetch_latest_price
from decimal import Decimal
from django.db import transaction

class Services:

    @transaction.atomic
    def buy_stock(self, user, symbol, quantity):
        symbol = symbol.upper().strip()

        quantity = Decimal(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        current_price = fetch_latest_price(symbol)
        if current_price is None:
            raise ValueError("Could not fetch current price for the symbol.")
        current_price = Decimal(current_price)

        if user.profile.current_cash_balance < current_price * quantity:
            raise ValueError("Insufficient funds to complete purchase.")
        # Deduct cash balance
        user.profile.current_cash_balance -= current_price * quantity
        user.profile.save()

        # Update trades
        Trades.objects.create(
            user=user,
            side=Trades.BUY,
            ticker=symbol,
            shares=quantity,
            exec_price=current_price
            )
        
        # Update holdings
        holding, created = Holdings.objects.get_or_create(user=user, ticker=symbol)
        total_cost = holding.avg_cost_basis * holding.quantity + current_price * quantity
        holding.quantity += quantity
        holding.avg_cost_basis = total_cost / holding.quantity
        holding.save()

    @transaction.atomic
    def sell_stock(self, user, symbol, quantity):
        symbol = symbol.upper().strip()

        quantity = Decimal(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
        
        current_price = fetch_latest_price(symbol)
        if current_price is None:
            raise ValueError("Could not fetch current price for the symbol.")
        current_price = Decimal(current_price)

        # Check holdings
        holding = Holdings.objects.filter(user=user, ticker=symbol).first()
        if holding is None or holding.quantity < quantity:
            raise ValueError("Insufficient holdings to sell.")
        
        # Add cash balance
        user.profile.current_cash_balance += current_price * quantity
        user.profile.save()
        
        # Update trades
        Trades.objects.create(
            user=user,
            side=Trades.SELL,
            ticker=symbol,
            shares=quantity,
            exec_price=current_price
            )
        
        # Update holdings
        holding.quantity -= quantity
        if holding.quantity == 0:
            holding.delete()
        else:
            holding.save()
        
