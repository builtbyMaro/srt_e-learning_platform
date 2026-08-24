from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .utils import check_field_values

# Create your views here.

def home_view(request):
    return render(request, 'main_app/index.html')

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        is_instructor = request.POST.get("is_instructor")

        if False in check_field_values([username, firstname, lastname, password, password2]):
            messages.error(request, "All fields are required")
            return redirect("mainapp:signup", permanent=True)

        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken")
            return redirect("mainapp:signup", permanent=True)
        
        if password != password2:
            messages.info(request, "Password does not match!")
            return redirect("mainapp:signup", permanent=True)
        
        user = User.objects.create_user(username=username, password=password, first_name=firstname, last_name=lastname)

        if is_instructor:
            profile = Profile.objects.create(user=user, is_instructor=True)
        else:
            profile = Profile.objects.create(user=user)
        messages.success(request, "Account created successfully.")
        return redirect("mainapp:login", permanent=True)

    # Return Sign up form for GET requests
    return render(request, 'main_app/signup.html')

def login_view(request):
    return render(request, 'main_app/login.html')