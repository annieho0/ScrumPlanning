from django.shortcuts import render, redirect
from .forms import RegisterFrom
from django.db import IntegrityError
from django.contrib.auth import login, authenticate

def admin_required(func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser:
            return func(request, *args, **kwargs)
        
        else:
            return redirect('/admin')
    
    return _wrapped_view

@admin_required
# Create your views here.
def register(response):
    if response.method == "POST":
        form = RegisterFrom(response.POST)
        if form.is_valid():
           
            form.save()
        else:
            raise IntegrityError("User information already exists.")
        return redirect("/admin/register/customizeduser")

    else:
        form = RegisterFrom()
    print("Hello")
    return render(response, "register/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        print(username, password)

        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
        else:
            return redirect("/login")