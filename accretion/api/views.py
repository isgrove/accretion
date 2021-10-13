from django.http import JsonResponse
from django.shortcuts import render
from app.models import Portfolio, Profile
from app.stocks import get_display_data


def get_portfolio(request):
    portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
    return JsonResponse(get_display_data(portfolio_id), safe=False)
