from django.conf.urls import url, include
from .views import signup, upload_portfolio_data, home

app_name = "app"

urlpatterns = [
    url("", include("django.contrib.auth.urls")),
    url("signup/", signup, name="signup"),
    url("account/portfolio/", upload_portfolio_data, name="upload"),
    url("", home, name="home"),
]