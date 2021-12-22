from django.conf.urls import url, include
from .views import get_portfolio, get_portfolio_1y, get_check_time


app_name = "api"

urlpatterns = [
    url("portfolio/", get_portfolio, name="api_portfolio"),
    url("portfolio-1y/", get_portfolio_1y, name="api_portfolio_1y"),
    url("time/", get_check_time, name="time"),
]