from django.contrib import messages
from django.contrib.auth import login
from django.core.files.storage import default_storage
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import CustomUserCreationForm, PortfolioDataForm


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
            return redirect(reverse("/"))


def upload_portfolio_data(request):
    if request.method == 'POST':
        form = PortfolioDataForm(request.POST, request.FILES)
        if form.is_valid():            
            new_file = request.FILES['csv_file']
            file_name = default_storage.save(new_file.name, new_file)
            messages.add_message(request, messages.SUCCESS, "You have successfully uploaded your portfolio data.")
            return redirect("/")
    else:
        form = PortfolioDataForm()
    return render(request, 'app/upload.html', {'form': form})