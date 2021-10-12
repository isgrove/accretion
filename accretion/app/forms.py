from django.contrib.auth.forms import UserCreationForm
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


class PortfolioDataForm(forms.Form):
    csv_file = forms.FileField()
    is_adjusted = forms.BooleanField(required=False)