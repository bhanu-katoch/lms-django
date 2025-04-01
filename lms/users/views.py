from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@never_cache
def user_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard")  # Redirect if already logged in
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            #messages.success(request, "Logged in successfully!")
            return redirect("dashboard")  # Change to your home page
        else:
            messages.error(request, "Invalid username or password!")

    response = render(request, "auth/login.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    return response
@csrf_exempt
def user_logout(request):
    logout(request)
    request.session.flush()  # Clear session completely
    messages.success(request, "Logged out successfully!")
    return redirect("login")

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "auth/register.html", {"form": form})
def home_user(request):
    return render(request,'home_user.html')