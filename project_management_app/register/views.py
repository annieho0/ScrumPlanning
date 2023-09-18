from django.shortcuts import render, redirect
from .forms import RegisterFrom
from django.db import IntegrityError
from .models import CustomizedUser
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
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        if form.is_valid():
            form.save()
        elif CustomizedUser.objects.filter(username=username).exists():
            raise IntegrityError("This username already exists.")
        elif CustomizedUser.objects.filter(email=email).exists():
            raise IntegrityError("This email already exists.")
        return redirect("/admin/auth/user")

    else:
        form = RegisterFrom()

    return render(response, "register/register.html", {"form": form})