from django.http import JsonResponse
from django.shortcuts import render
from app.models import Portfolio, Profile, Trade
from app.stocks import get_portfolio_data

import asyncio


def get_portfolio(request):
    portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
    symbols = list(Trade.objects.values("symbol").filter(portfolio_id = portfolio_id).distinct())
    raw_trade_data = list(Trade.objects.filter(portfolio_id = portfolio_id))
    data = asyncio.run(get_portfolio_data(symbols, raw_trade_data))
    return JsonResponse(data, safe=False)