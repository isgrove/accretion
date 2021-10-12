from django.contrib.auth.forms import UserCreationForm
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)


class PortfolioDataForm(forms.Form):
    csv_file = forms.FileField()
    is_adjusted = forms.BooleanField(required=False)


class AccountSettingsForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs=
        {'class': 'rounded p-1 px-2 border-solid border border-gray-50 border-opacity-50 focus:border-blue-800 focus:border-opacity-100'}
    ))
    last_name = forms.CharField(widget=forms.TextInput(attrs=
        {'class': 'rounded p-1 px-2 border-solid border border-gray-50 border-opacity-50'}
    ))
    email = forms.EmailField(widget=forms.EmailInput(attrs=
        {'class': 'rounded p-1 px-2 border-solid border border-gray-50 border-opacity-50'}
    ))