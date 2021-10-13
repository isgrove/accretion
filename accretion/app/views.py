from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import CustomUserCreationForm, PortfolioDataForm, AccountSettingsForm
from .stocks import upload_portfolio, get_display_data
from .models import Profile, Portfolio


def signup(request):
    if request.method == "GET":
        return render(
            request, "app/signup.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("app:home")


def home(request):
    if request.user.is_authenticated:
        return redirect("app:dashboard") #TODO: change to dashboard
    else:
        return render(
            request,
            "app/home.html",
        )


def dashboard(request):
    return render(
        request,
        "app/dashboard.html",
    )


def portfolio(request):
    # portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
    # get_display_data(portfolio_id)
    return render(
        request,
        "app/portfolio.html"
    )


def settings(request):
    user = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        form = AccountSettingsForm(request.POST)
        if form.is_valid():
            User.objects.filter(id=request.user.id).update(
                first_name = form.cleaned_data['first_name'],
                last_name = form.cleaned_data['last_name'],
                email = form.cleaned_data['email'],
            )
    else:
        form = AccountSettingsForm(initial={
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            })
    return render(
        request,
        "app/settings.html",
        {'form': form},
    )



def upload_portfolio_data(request):
    if request.method == 'POST':
        form = PortfolioDataForm(request.POST, request.FILES)
        if form.is_valid():
            new_file = request.FILES['csv_file']
            file_name = default_storage.save(new_file.name, new_file)
            portfolio_id = Portfolio.objects.get(owner_id=Profile.objects.get(user_id=request.user.id).id).id
            is_adjusted = form.cleaned_data['is_adjusted']
            upload_portfolio(file_name, portfolio_id, is_adjusted)

            messages.add_message(request, messages.SUCCESS, "You have successfully uploaded your portfolio data.")
            return redirect("app:home")
    else:
        form = PortfolioDataForm()
    return render(request, 'app/upload.html', {'form': form})