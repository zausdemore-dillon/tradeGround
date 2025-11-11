from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from trades.models import Holdings
from trades.services import Services

@method_decorator(login_required, name='dispatch')
class SellView(View):
    def get(self, request):
        # Get user's current holdings from database
        holdings = Holdings.objects.filter(user=request.user, quantity__gt=0)
        
        context = {
            'holdings': holdings
        }
        return render(request, 'sell/sell.html', context)
    
    def post(self, request):
        # Handle sell form submission
        symbol = request.POST.get('symbol')
        quantity = request.POST.get('quantity')
        
        try:
            # Use the Services class to handle the sell
            services = Services()
            services.sell_stock(request.user, symbol, quantity)
            
            messages.success(request, f'Successfully sold {quantity} shares of {symbol}!')
            
        except ValueError as e:
            # Catch validation errors (insufficient holdings, bad quantity, etc.)
            messages.error(request, str(e))
            
        except Exception as e:
            # Catch any other errors
            messages.error(request, f'Error selling stock: {str(e)}')
        
        return redirect('/sell/')