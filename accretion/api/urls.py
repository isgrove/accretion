from django.conf.urls import url, include
from .views import get_portfolio


app_name = "api"

urlpatterns = [
    url("portfolio/", get_portfolio, name="api_portfolio"),
]