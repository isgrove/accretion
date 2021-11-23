from django.http import JsonResponse
from django.shortcuts import render
from app.models import Portfolio, Profile, Trade
from .stocks import get_portfolio_data, get_portfolio_data_1y

import asyncio


def get_portfolio(request):
    portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
    symbols = list(Trade.objects.values("symbol").filter(portfolio_id = portfolio_id).distinct().order_by('symbol'))
    raw_trade_data = list(Trade.objects.filter(portfolio_id = portfolio_id).order_by('symbol'))
    data = asyncio.run(get_portfolio_data(symbols, raw_trade_data))
    return JsonResponse(data, safe=False)


def get_portfolio_1y(request):
    portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
    symbols = list(Trade.objects.values("symbol").filter(portfolio_id = portfolio_id).distinct().order_by('symbol'))
    raw_trade_data = list(Trade.objects.filter(portfolio_id = portfolio_id).order_by('symbol'))
    data = asyncio.run(get_portfolio_data_1y(symbols, raw_trade_data))
    return JsonResponse(data, safe=False)