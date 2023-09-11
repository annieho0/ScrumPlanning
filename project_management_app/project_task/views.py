from django.shortcuts import render, redirect


# Create your views here.
def home(response):
    """This view renders the home page"""
    return render(response, "project_task/Home.html", {"name": "home"})


def home_redirect(response):
    """This view redirects the user to the home page when they visit the root URL"""
    return redirect("home/")


def project_backlog(response):
    """This view renders the project backlog page"""
    return render(response, "project_task/project_backlog.html", {"name": "project_backlog"})
