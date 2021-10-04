from django.conf.urls import url, include
from .views import signup


app_name = "app"

urlpatterns = [
    url("", include("django.contrib.auth.urls")),
    url("signup/", signup, name="signup"),
]